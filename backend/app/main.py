"""FastAPI 服务入口：中间件（日志+限流）+ 会话管理 + 全部对话接口"""
import json
import logging
import time
from collections import defaultdict

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.orm import Session

from app import memory
from app.agent import agent_chat
from app.config import RATE_LIMIT, SYSTEM_PROMPT
from app.database import SessionLocal, init_db
from app.llm import chat, classify_intent, llm, to_messages
from app.schemas import (ChatRequest, ChatResponse, MessageOut,
                         SessionOut, SessionTitleUpdate)

# ============ 日志配置：线上排查问题的唯一依靠 ============
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("smart-chat")

init_db()   # 启动时自动建表

app = FastAPI(title="店小智智能客服 API", version="2.0.0")

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


# ============ 会话管理接口 ============
@app.get("/api/sessions", response_model=list[SessionOut])
def list_sessions_api(db: Session = Depends(get_db)):
    """会话列表（前端侧边栏用）"""
    return memory.list_sessions(db)


@app.post("/api/sessions", response_model=SessionOut)
def create_session_api(db: Session = Depends(get_db)):
    """新建会话"""
    return memory.create_session(db)


@app.delete("/api/sessions/{session_id}", response_model=ChatResponse)
def delete_session_api(session_id: str, db: Session = Depends(get_db)):
    """删除会话及其全部消息"""
    if not memory.delete_session(db, session_id):
        raise HTTPException(status_code=404, detail="会话不存在")
    return ChatResponse(code=0, message="已删除", data={})


@app.patch("/api/sessions/{session_id}", response_model=SessionOut)
def rename_session_api(session_id: str, req: SessionTitleUpdate, db: Session = Depends(get_db)):
    """修改会话标题"""
    if not memory.rename_session(db, session_id, req.title):
        raise HTTPException(status_code=404, detail="会话不存在")
    db_session = db.get(memory.ChatSession, session_id)
    return db_session


@app.get("/api/sessions/{session_id}/messages", response_model=list[MessageOut])
def get_messages_api(session_id: str, db: Session = Depends(get_db)):
    """某会话的全部历史消息（前端切换会话时恢复聊天记录）"""
    return memory.get_messages(db, session_id)


# ============ 对话接口 ============
@app.post("/api/chat", response_model=ChatResponse)
def chat_api(req: ChatRequest, db: Session = Depends(get_db)):
    """多轮对话：取历史 → 带历史调模型 → 结果落库"""
    try:
        history = memory.get_history(db, req.session_id)       # 1. 取历史
        reply = chat(req.message, history)                     # 2. 带历史问大模型
        memory.append(db, req.session_id, req.message, reply)  # 3. 本轮写入数据库
        return ChatResponse(code=0, message="success", data={"reply": reply})
    except Exception as e:
        logger.error(f"/api/chat 异常: {e}")
        # 兜底：不让异常堆栈直接暴露给前端（安全要求）
        return ChatResponse(code=500, message=f"AI 服务异常：{str(e)}", data={"reply": ""})


@app.post("/api/agent/chat", response_model=ChatResponse)
def agent_chat_api(req: ChatRequest, db: Session = Depends(get_db)):
    """智能体对话：工具调用 + 记忆持久化，结果同步写入业务库供前端展示"""
    try:
        result = agent_chat(req.message, req.session_id)
        # 双写：工具调用记录拼进回复一起落库（刷新页面也能看到）
        tools = result["tools_used"]
        record = (f"🔧 [调用工具：{'、'.join(tools)}]\n\n" + result["reply"]) if tools else result["reply"]
        memory.append(db, req.session_id, req.message, record)
        return ChatResponse(code=0, message="success", data={
            "reply": result["reply"],
            "tools_used": tools,   # 返回工具记录，前端实时展示
        })
    except Exception as e:
        logger.error(f"/api/agent/chat 异常: {e}")
        return ChatResponse(code=500, message=f"智能体服务异常：{str(e)}", data={"reply": ""})


@app.post("/api/smart/chat", response_model=ChatResponse)
def smart_chat_api(req: ChatRequest, db: Session = Depends(get_db)):
    """统一入口：先意图识别，再自动路由到普通对话或智能体"""
    try:
        intent = classify_intent(req.message)
        if intent == "agent":
            result = agent_chat(req.message, req.session_id)
            tools = result["tools_used"]
            record = (f"🔧 [调用工具：{'、'.join(tools)}]\n\n" + result["reply"]) if tools else result["reply"]
            memory.append(db, req.session_id, req.message, record)
            return ChatResponse(code=0, message="success", data={
                "route": "agent", "reply": result["reply"], "tools_used": tools,
            })
        history = memory.get_history(db, req.session_id)
        reply = chat(req.message, history)
        memory.append(db, req.session_id, req.message, reply)
        return ChatResponse(code=0, message="success", data={"route": "chat", "reply": reply})
    except Exception as e:
        logger.error(f"/api/smart/chat 异常: {e}")
        return ChatResponse(code=500, message=f"服务异常：{str(e)}", data={"reply": ""})


@app.post("/api/chat/stream")
async def chat_stream_api(req: ChatRequest, db: Session = Depends(get_db)):
    """流式对话接口（SSE）：逐字推送 AI 回复"""
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    messages.extend(to_messages(memory.get_history(db, req.session_id)))
    messages.append(HumanMessage(content=req.message))

    async def event_generator():
        full_reply = ""
        try:
            async for chunk in llm.astream(messages):     # 异步流式接收
                if chunk.content:
                    full_reply += chunk.content
                    # SSE 格式：data: xxx\n\n（json.dumps 防止内容含换行破坏格式）
                    yield f"data: {json.dumps({'delta': chunk.content}, ensure_ascii=False)}\n\n"
            memory.append(db, req.session_id, req.message, full_reply)   # 完整回复落库
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
