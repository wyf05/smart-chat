"""FastAPI 服务入口：认证 + 中间件（日志+限流）+ 会话/对话/业务数据/统计全部接口"""
import json
import logging
import time
from collections import defaultdict

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.messages import AIMessageChunk, HumanMessage, SystemMessage
from sqlalchemy.orm import Session

from app import catalog, memory, stats
from app.agent import agent_chat, get_agent_async
from app.config import RATE_LIMIT, SYSTEM_PROMPT
from app.database import SessionLocal, init_db
from app.llm import chat, classify_intent, llm, to_messages
from app.models import User
from app.schemas import (ChatRequest, ChatResponse, CouponIn, KnowledgeIn,
                         LoginRequest, MessageOut, OrderIn, SessionOut,
                         SessionTitleUpdate)
from app.security import create_token, hash_password, verify_token

# ============ 日志配置：线上排查问题的唯一依靠 ============
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("smart-chat")

init_db()   # 启动时自动建表/迁移/种子数据

app = FastAPI(title="店小智智能客服 API", version="3.0.0")

# CORS 跨域：前端(5173端口)与后端(8000端口)不同源，必须放行才能互相访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 学习阶段放开所有来源；生产环境应填具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 依赖注入：每个请求自动分配一个数据库连接，用完自动回收 ============
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============ 日志中间件：每个请求自动记录路径、状态码、耗时 ============
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    cost = (time.time() - start) * 1000
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} 耗时 {cost:.0f}ms")
    return response


# ============ 限流中间件：滑动窗口，每 IP 每分钟最多 RATE_LIMIT 次 /api 请求 ============
_rate_store: dict[str, list[float]] = defaultdict(list)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        _rate_store[ip] = [t for t in _rate_store[ip] if now - t < 60]   # 清理 1 分钟前的记录
        if len(_rate_store[ip]) >= RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"code": 429, "message": "请求过于频繁，请稍后再试"},
            )
        _rate_store[ip].append(now)
    return await call_next(request)


@app.get("/")
def index():
    """健康检查：运维探活用"""
    return {"message": "店小智智能客服后端运行中，接口文档见 /docs"}


# ============ 认证接口（无需 token）============
@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """账号登录：校验通过后签发 JWT"""
    user = db.get(User, req.username)
    if not user or user.password_hash != hash_password(req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {"code": 0, "message": "success",
            "data": {"token": create_token(user.username), "username": user.username}}


# ============ 会话管理接口（需登录）============
@app.get("/api/sessions", response_model=list[SessionOut],
         dependencies=[Depends(verify_token)])
def list_sessions_api(db: Session = Depends(get_db)):
    """会话列表（前端侧边栏用）"""
    return memory.list_sessions(db)


@app.post("/api/sessions", response_model=SessionOut,
          dependencies=[Depends(verify_token)])
def create_session_api(db: Session = Depends(get_db)):
    """新建会话"""
    return memory.create_session(db)


@app.delete("/api/sessions/{session_id}", response_model=ChatResponse,
            dependencies=[Depends(verify_token)])
def delete_session_api(session_id: str, db: Session = Depends(get_db)):
    """删除会话及其全部消息"""
    if not memory.delete_session(db, session_id):
        raise HTTPException(status_code=404, detail="会话不存在")
    return ChatResponse(code=0, message="已删除", data={})


@app.patch("/api/sessions/{session_id}", response_model=SessionOut,
           dependencies=[Depends(verify_token)])
def rename_session_api(session_id: str, req: SessionTitleUpdate, db: Session = Depends(get_db)):
    """修改会话标题"""
    if not memory.rename_session(db, session_id, req.title):
        raise HTTPException(status_code=404, detail="会话不存在")
    return db.get(memory.ChatSession, session_id)


@app.get("/api/sessions/{session_id}/messages", response_model=list[MessageOut],
         dependencies=[Depends(verify_token)])
def get_messages_api(session_id: str, db: Session = Depends(get_db)):
    """某会话的全部历史消息（前端切换会话时恢复聊天记录）"""
    return memory.get_messages(db, session_id)


# ============ 业务数据中心：订单（需登录）============
@app.get("/api/orders", dependencies=[Depends(verify_token)])
def list_orders_api(db: Session = Depends(get_db)):
    """订单列表"""
    return [{"order_id": o.order_id, "status": o.status, "amount": o.amount,
             "receiver": o.receiver, "logistics": o.logistics} for o in catalog.list_orders(db)]


@app.post("/api/orders", dependencies=[Depends(verify_token)])
def save_order_api(req: OrderIn, db: Session = Depends(get_db)):
    """新增/修改订单（智能体查询的即时数据源）"""
    o = catalog.upsert_order(db, req.order_id, req.status, req.amount,
                             req.receiver, req.logistics)
    return ChatResponse(code=0, message="success", data={"order_id": o.order_id})


@app.delete("/api/orders/{order_id}", dependencies=[Depends(verify_token)])
def delete_order_api(order_id: str, db: Session = Depends(get_db)):
    if not catalog.delete_order(db, order_id):
        raise HTTPException(status_code=404, detail="订单不存在")
    return ChatResponse(code=0, message="已删除", data={})


# ============ 业务数据中心：优惠券（需登录）============
@app.get("/api/coupons", dependencies=[Depends(verify_token)])
def list_coupons_api(db: Session = Depends(get_db)):
    """优惠券列表"""
    return [{"code": c.code, "title": c.title, "discount": c.discount,
             "valid_until": c.valid_until, "status": c.status} for c in catalog.list_coupons(db)]


@app.post("/api/coupons", dependencies=[Depends(verify_token)])
def save_coupon_api(req: CouponIn, db: Session = Depends(get_db)):
    """新增/修改优惠券"""
    c = catalog.upsert_coupon(db, req.code, req.title, req.discount,
                              req.valid_until, req.status)
    return ChatResponse(code=0, message="success", data={"code": c.code})


@app.delete("/api/coupons/{code}", dependencies=[Depends(verify_token)])
def delete_coupon_api(code: str, db: Session = Depends(get_db)):
    if not catalog.delete_coupon(db, code):
        raise HTTPException(status_code=404, detail="优惠券不存在")
    return ChatResponse(code=0, message="已删除", data={})


# ============ 业务数据中心：知识库（需登录）============
@app.get("/api/knowledge", dependencies=[Depends(verify_token)])
def list_knowledge_api(db: Session = Depends(get_db)):
    """知识库条目列表"""
    return [{"id": k.id, "question": k.question, "answer": k.answer,
             "keywords": k.keywords} for k in catalog.list_knowledge(db)]


@app.post("/api/knowledge", dependencies=[Depends(verify_token)])
def add_knowledge_api(req: KnowledgeIn, db: Session = Depends(get_db)):
    """新增知识条目"""
    k = catalog.add_knowledge(db, req.question, req.answer, req.keywords)
    return ChatResponse(code=0, message="success", data={"id": k.id})


@app.put("/api/knowledge/{item_id}", dependencies=[Depends(verify_token)])
def update_knowledge_api(item_id: int, req: KnowledgeIn, db: Session = Depends(get_db)):
    """修改知识条目"""
    if not catalog.update_knowledge(db, item_id, req.question, req.answer, req.keywords):
        raise HTTPException(status_code=404, detail="知识条目不存在")
    return ChatResponse(code=0, message="success", data={})


@app.delete("/api/knowledge/{item_id}", dependencies=[Depends(verify_token)])
def delete_knowledge_api(item_id: int, db: Session = Depends(get_db)):
    if not catalog.delete_knowledge(db, item_id):
        raise HTTPException(status_code=404, detail="知识条目不存在")
    return ChatResponse(code=0, message="已删除", data={})


# ============ 统计接口（需登录）============
@app.get("/api/stats/overview", dependencies=[Depends(verify_token)])
def stats_overview_api(db: Session = Depends(get_db)):
    """首页仪表盘与统计页共用的聚合数据"""
    return stats.overview(db)


# ============ 对话接口（需登录；每次调用写入统计埋点）============
@app.post("/api/chat", response_model=ChatResponse, dependencies=[Depends(verify_token)])
def chat_api(req: ChatRequest, db: Session = Depends(get_db)):
    """多轮对话：取历史 → 带历史调模型 → 结果落库"""
    t0 = time.time()
    try:
        history = memory.get_history(db, req.session_id)       # 1. 取历史
        reply = chat(req.message, history)                     # 2. 带历史问大模型
        duration = int((time.time() - t0) * 1000)
        memory.append(db, req.session_id, req.message, reply,
                      route="chat", duration_ms=duration)      # 3. 落库 + 埋点
        return ChatResponse(code=0, message="success", data={"reply": reply})
    except Exception as e:
        logger.error(f"/api/chat 异常: {e}")
        # 兜底：不让异常堆栈直接暴露给前端（安全要求）
        return ChatResponse(code=500, message=f"AI 服务异常：{str(e)}", data={"reply": ""})


@app.post("/api/agent/chat", response_model=ChatResponse, dependencies=[Depends(verify_token)])
def agent_chat_api(req: ChatRequest, db: Session = Depends(get_db)):
    """智能体对话：工具调用 + 记忆持久化，结果同步写入业务库供前端展示"""
    t0 = time.time()
    try:
        result = agent_chat(req.message, req.session_id)
        tools = result["tools_used"]
        duration = int((time.time() - t0) * 1000)
        # 双写：工具调用记录拼进回复一起落库（刷新页面也能看到）
        record = (f"🔧 [调用工具：{'、'.join(tools)}]\n\n" + result["reply"]) if tools else result["reply"]
        memory.append(db, req.session_id, req.message, record,
                      route="agent", tools=tools, duration_ms=duration)
        return ChatResponse(code=0, message="success", data={
            "reply": result["reply"],
            "tools_used": tools,   # 返回工具记录，前端实时展示
        })
    except Exception as e:
        logger.error(f"/api/agent/chat 异常: {e}")
        return ChatResponse(code=500, message=f"智能体服务异常：{str(e)}", data={"reply": ""})


@app.post("/api/smart/chat", response_model=ChatResponse, dependencies=[Depends(verify_token)])
def smart_chat_api(req: ChatRequest, db: Session = Depends(get_db)):
    """统一入口：先意图识别，再自动路由到普通对话或智能体"""
    t0 = time.time()
    try:
        intent = classify_intent(req.message)
        if intent == "agent":
            result = agent_chat(req.message, req.session_id)
            tools = result["tools_used"]
            duration = int((time.time() - t0) * 1000)
            record = (f"🔧 [调用工具：{'、'.join(tools)}]\n\n" + result["reply"]) if tools else result["reply"]
            memory.append(db, req.session_id, req.message, record,
                          route="agent", tools=tools, duration_ms=duration)
            return ChatResponse(code=0, message="success", data={
                "route": "agent", "reply": result["reply"], "tools_used": tools,
            })
        history = memory.get_history(db, req.session_id)
        reply = chat(req.message, history)
        duration = int((time.time() - t0) * 1000)
        memory.append(db, req.session_id, req.message, reply,
                      route="chat", duration_ms=duration)
        return ChatResponse(code=0, message="success", data={"route": "chat", "reply": reply})
    except Exception as e:
        logger.error(f"/api/smart/chat 异常: {e}")
        return ChatResponse(code=500, message=f"服务异常：{str(e)}", data={"reply": ""})


# ============ 流式对话接口（SSE）：三挡共用一套事件协议 ============
# 事件：{type:'delta',text} 正文增量 | {type:'tool',name} 工具调用 |
#       {type:'route',route} 自动挡路由结果 | {type:'error',message}；结束发 [DONE]

def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"


async def _chat_event_gen(req: ChatRequest, db: Session):
    """普通对话流：glm-4-flash 逐字推送，结束落库埋点"""
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    messages.extend(to_messages(memory.get_history(db, req.session_id)))
    messages.append(HumanMessage(content=req.message))
    full_reply, t0 = "", time.time()
    try:
        async for chunk in llm.astream(messages):     # 异步流式接收
            if chunk.content:
                full_reply += chunk.content
                yield _sse({"type": "delta", "text": chunk.content})
        duration = int((time.time() - t0) * 1000)
        memory.append(db, req.session_id, req.message, full_reply,
                      route="chat", duration_ms=duration)   # 完整回复落库 + 埋点
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield _sse({"type": "error", "message": str(e)})


async def _agent_event_gen(req: ChatRequest, db: Session):
    """智能体流：astream 逐 token 转发；工具调用发独立事件；结束落库埋点（与非流式一致）"""
    config = {"configurable": {"thread_id": req.session_id}}
    full_reply, tools_used, t0 = "", [], time.time()
    try:
        async for chunk, _meta in get_agent_async().astream(
            {"messages": [{"role": "user", "content": req.message}]},
            config, stream_mode="messages",
        ):
            if not isinstance(chunk, AIMessageChunk):
                continue                            # ToolMessage 等不是模型 token，跳过
            for tc in chunk.tool_call_chunks:       # 工具名随流式片段到达，去重发事件
                name = tc.get("name")
                if name and name not in tools_used:
                    tools_used.append(name)
                    yield _sse({"type": "tool", "name": name})
            if chunk.content:
                text = chunk.content if isinstance(chunk.content, str) else "".join(
                    p.get("text", "") for p in chunk.content if isinstance(p, dict))
                if text:
                    full_reply += text
                    yield _sse({"type": "delta", "text": text})
        if "</think>" in full_reply:                # 与非流式一致的兜底清洗
            full_reply = full_reply.split("</think>")[-1]
        record = (f"🔧 [调用工具：{'、'.join(tools_used)}]\n\n" + full_reply) if tools_used else full_reply
        memory.append(db, req.session_id, req.message, record,
                      route="agent", tools=tools_used,
                      duration_ms=int((time.time() - t0) * 1000))
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield _sse({"type": "error", "message": str(e)})


@app.post("/api/chat/stream", dependencies=[Depends(verify_token)])
async def chat_stream_api(req: ChatRequest, db: Session = Depends(get_db)):
    """普通对话流式接口（SSE）：逐字推送 AI 回复"""
    return StreamingResponse(_chat_event_gen(req, db), media_type="text/event-stream")


@app.post("/api/agent/chat/stream", dependencies=[Depends(verify_token)])
async def agent_chat_stream_api(req: ChatRequest, db: Session = Depends(get_db)):
    """智能体流式接口（SSE）：工具调用与正文增量分事件推送"""
    return StreamingResponse(_agent_event_gen(req, db), media_type="text/event-stream")


@app.post("/api/smart/chat/stream", dependencies=[Depends(verify_token)])
async def smart_chat_stream_api(req: ChatRequest, db: Session = Depends(get_db)):
    """自动挡流式接口（SSE）：先推路由结果，再转发对应链路的事件流"""
    async def smart_event_generator():
        intent = classify_intent(req.message)
        yield _sse({"type": "route", "route": intent})
        gen = _agent_event_gen(req, db) if intent == "agent" else _chat_event_gen(req, db)
        async for ev in gen:
            yield ev

    return StreamingResponse(smart_event_generator(), media_type="text/event-stream")
