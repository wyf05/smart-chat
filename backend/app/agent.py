"""智能体模块：LangChain 实现带工具调用与持久记忆的客服智能体

工具的数据来源：订单/优惠券/知识库来自业务数据库（orders/coupons/knowledge 表），
天气来自高德开放平台实时 API。在"业务数据中心"页面修改数据后，
智能体的回答会同步变化。
"""
import sqlite3
from datetime import datetime

import requests

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver

from app.catalog import (query_coupon_by_code, query_order_by_id,
                         search_knowledge as search_knowledge_db)
from app.config import (AGENT_DB_PATH, AGENT_MODEL, AMAP_KEY, API_KEY,
                        BASE_URL)
from app.database import SessionLocal


@tool
def query_order(order_id: str) -> str:
    """根据订单号查询订单的状态、金额、收件人与物流信息。参数 order_id 是订单号，格式如 "DD20260001"。
    用户询问订单进度、物流、发货、签收情况时必须使用本工具。"""
    db = SessionLocal()
    try:
        return query_order_by_id(db, order_id)   # 数据来源：业务数据库 orders 表
    finally:
        db.close()


@tool
def get_weather(city: str) -> str:
    """查询指定中国城市当前的实时天气。参数 city 是城市名，如"长沙"。
    用户询问天气、是否适合发货/出行时使用本工具。"""
    if not AMAP_KEY:
        return "天气服务未配置：请在 backend/.env 的 AMAP_KEY 中填入高德开放平台的 Key（Web服务类型）"
    try:
        # 高德天气接口只认 adcode（6 位行政区划码），先用地理解码把城市名换成 adcode
        geo = requests.get(
            "https://restapi.amap.com/v3/geocode/geo",
            params={"key": AMAP_KEY, "address": city},
            timeout=5,
        ).json()
        geocodes = geo.get("geocodes") or []
        if geo.get("status") != "1" or not geocodes:
            if geo.get("info") in ("INVALID_USER_KEY", "USERKEY_PLAT_NOMATCH"):
                # Key 无效或不是 Web 服务类型时，geocode 这一步就会失败
                return f"天气查询失败：{geo.get('info')}（请检查 AMAP_KEY 是否为高德「Web服务」类型的 Key）"
            return f"没有找到城市「{city}」，请确认城市名（如：长沙、上海）"
        adcode = geocodes[0]["adcode"]
        # 再查实时天气（extensions=base 为实况，forecast 为预报）
        data = requests.get(
            "https://restapi.amap.com/v3/weather/weatherInfo",
            params={"key": AMAP_KEY, "city": adcode, "extensions": "base"},
            timeout=5,
        ).json()
        lives = data.get("lives") or []
        if data.get("status") != "1" or not lives:
            # Key 类型错误/配额用尽等情况，高德会在 info 里给原因
            return f"天气查询失败：{data.get('info', '接口返回异常')}（请检查 AMAP_KEY 是否为 Web 服务类型）"
        w = lives[0]
        return (f"{w['city']}当前天气：{w['weather']}，气温 {w['temperature']}℃，"
                f"{w['winddirection']}风 {w['windpower']} 级，湿度 {w['humidity']}%"
                f"（数据来源：高德开放平台，更新于 {w['reporttime']}）")
    except requests.RequestException as e:
        return f"天气查询网络异常：{e}"


@tool
def calculate(expression: str) -> str:
    """计算数学表达式的精确结果。参数 expression 是算式，如 "3874*239"。
    遇到任何数学计算都必须使用本工具精确计算，禁止口算估算。"""
    try:
        # 只允许数字和运算符，防止危险代码注入（安全铁律：不信任任何外部输入）
        allowed = set("0123456789+-*/.() ")
        if not set(expression) <= allowed:
            return "表达式含有非法字符"
        return f"{expression} = {eval(expression)}"
    except Exception as e:
        return f"计算失败：{e}"


@tool
def get_current_time() -> str:
    """获取当前日期和时间。用户问"现在几点""今天几号"等问题时使用。"""
    return datetime.now().strftime("现在是 %Y年%m月%d日 %H:%M:%S")


@tool
def get_coupon(code: str) -> str:
    """根据优惠券码查询优惠券的名称、面额、有效期与状态。参数 code 是券码，格式如 "QUAN100"。
    用户询问优惠券、优惠码、折扣券是否可用、面额、有效期时必须使用本工具。"""
    db = SessionLocal()
    try:
        return query_coupon_by_code(db, code)    # 数据来源：业务数据库 coupons 表
    finally:
        db.close()


@tool
def search_knowledge(query: str) -> str:
    """检索商家知识库（售后政策、发货时间、付款方式、发票等常见问题）。
    参数 query 是与问题相关的关键词或原问题。
    用户咨询店铺规则、售后政策、发货付款发票等业务问题时必须优先使用本工具；
    检索到内容时回答需注明"来自知识库"，未检索到时如实告知并正常回答。"""
    db = SessionLocal()
    try:
        items = search_knowledge_db(db, query)   # 数据来源：业务数据库 knowledge_items 表
        if not items:
            return "知识库中未检索到相关内容"
        parts = [f"【{it.question}】{it.answer}" for it in items]
        return "知识库检索结果：" + " ｜ ".join(parts)
    finally:
        db.close()


TOOLS = [query_order, get_weather, calculate, get_current_time, get_coupon, search_knowledge]

# 智能体专用模型：温度 0（工具调用是精确动作，要稳定不要发散）
# extra_body 关闭 glm-4.5-flash 的思考模式：客服回复不需要展示推理过程，还能显著降低延迟
agent_llm = ChatOpenAI(
    model=AGENT_MODEL, api_key=API_KEY, base_url=BASE_URL, temperature=0,
    extra_body={"thinking": {"type": "disabled"}},
)

# 记忆持久化：SqliteSaver 把智能体每轮状态存入文件，重启不丢
_conn = sqlite3.connect(AGENT_DB_PATH, check_same_thread=False)
checkpointer = SqliteSaver(_conn)

# 组装智能体：ReAct 循环由 create_agent 内部自动完成
agent = create_agent(
    model=agent_llm,
    tools=TOOLS,
    system_prompt=(
        "你是「店小智」，一家电商公司的智能客服。"
        "用户的问题涉及订单查询、天气、当前时间、优惠券、数学计算、店铺售后政策时，"
        "必须调用对应工具获取真实结果，禁止编造；"
        "其他问题用简体中文礼貌、简洁地回答，不要为了调用工具而调用工具。"
    ),
    checkpointer=checkpointer,   # 传 thread_id 即自动带上历史记忆
)


def agent_chat(message: str, session_id: str) -> dict:
    """
    智能体对话入口。
    :param session_id: 会话ID（即 thread_id，同一会话共享记忆）
    :return: {"reply": 最终回复, "tools_used": [本轮调用过的工具名]}
    """
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config={"configurable": {"thread_id": session_id}},
    )

    msgs = result["messages"]
    reply = ""
    tools_used = []
    # msgs 是整个线程的全量消息流（SqliteSaver 会带回历史），因此：
    # 回复取最后一条有内容的 AI 消息；工具调用只统计最后一轮（最后一条用户消息之后）
    for msg in reversed(msgs):
        if msg.type == "ai" and msg.content and not reply:
            reply = msg.content
    # 兜底清洗：若模型仍返回思考痕迹（<think>...</think>），只保留最终回答
    if reply and "</think>" in reply:
        reply = reply.split("</think>")[-1]
    reply = (reply or "").strip() or "（智能体未返回内容）"
    last_user_idx = max(i for i, m in enumerate(msgs) if m.type == "human")
    for msg in msgs[last_user_idx:]:
        if msg.type == "ai" and getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                if tc["name"] not in tools_used:   # 去重：模型偶尔会重复调用同一工具
                    tools_used.append(tc["name"])

    return {"reply": reply, "tools_used": tools_used}
