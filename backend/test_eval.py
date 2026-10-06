"""智能体评估：工具选择正确率。运行：python test_eval.py
注意：每个用例都会真实调用大模型 API，有少量费用。
"""
from app.agent import agent_chat

# (问题, 期望调用的工具；None 表示期望不调用任何工具)
CASES = [
    ("订单DD20260001到哪了？", "query_order"),
    ("我的订单DD20260003签收了吗", "query_order"),
    ("长沙今天天气怎么样？", "get_weather"),
    ("北京会下雨吗？要不要带伞", "get_weather"),
    ("计算 1234*5678 等于多少", "calculate"),
    ("3.5 乘以 12 是多少", "calculate"),
    ("现在几点了？", "get_current_time"),
    ("今天几号？", "get_current_time"),
    ("优惠券QUAN100还能用吗", "get_coupon"),
    ("帮我查一下QUANVIP的状态", "get_coupon"),
    ("用一句话介绍你自己", None),
    ("Python 和 Java 的区别是什么", None),
]

import time

correct = 0
total_ms = 0.0
for i, (q, expected) in enumerate(CASES):
    t0 = time.time()
    r = agent_chat(q, session_id=f"eval-{i}")   # 每个用例独立会话，避免记忆串扰
    cost = (time.time() - t0) * 1000
    total_ms += cost
    used = r["tools_used"]
    ok = (expected in used) if expected else (len(used) == 0)
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] Q: {q[:20]:<24} 期望: {expected or '无工具':<16} 实际: {used or '无'}  耗时 {cost:.0f}ms")
    correct += ok

n = len(CASES)
print(f"\n工具选择正确率: {correct}/{n} = {correct / n:.0%}")
print(f"平均响应延迟: {total_ms / n:.0f}ms")
