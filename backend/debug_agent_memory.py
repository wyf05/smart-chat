# -*- coding: utf-8 -*-
"""对比不同模型在智能体场景下的记忆召回能力"""
import os
from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI


@tool
def query_order(order_id: str) -> str:
    """根据订单号查询订单的物流状态。参数 order_id 是订单号，格式如 "DD20260001"。"""
    orders = {
        "DD20260001": "已发货，顺丰速运，预计明天 18:00 前送达",
        "DD20260002": "待付款，订单金额 129.00 元",
    }
    return orders.get(order_id, f"未找到订单 {order_id}")


import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect(":memory:", check_same_thread=False)

for model_name in ("glm-4-flash", "glm-4.5-flash"):
    llm = ChatOpenAI(model=model_name, api_key=os.getenv("LLM_API_KEY"),
                     base_url=os.getenv("LLM_BASE_URL"), temperature=0)
    conn2 = sqlite3.connect(":memory:", check_same_thread=False)
    agent = create_agent(model=llm, tools=[query_order],
                         system_prompt="你是电商客服，涉及订单问题必须调用工具。",
                         checkpointer=SqliteSaver(conn2))
    agent.invoke({"messages": [{"role": "user", "content": "订单 DD20260001 到哪了？"}]},
                 config={"configurable": {"thread_id": "t1"}})
    r = agent.invoke({"messages": [{"role": "user", "content": "我们刚才聊的第一个订单号是多少？"}]},
                     config={"configurable": {"thread_id": "t1"}})
    reply = r["messages"][-1].content
    print(f"[{model_name}] 记忆召回: {reply[:60]}")
