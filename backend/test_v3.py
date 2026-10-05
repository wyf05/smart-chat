# -*- coding: utf-8 -*-
"""v3 新接口冒烟测试：登录鉴权 / 业务数据 CRUD / 知识库工具 / 统计埋点"""
import json
import urllib.request

BASE = "http://127.0.0.1:8000"


def call(method, path, body=None, token=None, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = resp.read().decode("utf-8")
            return resp.status, (payload if raw else json.loads(payload))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


# 1. 未带 token 访问受保护接口 -> 401
code, r = call("GET", "/api/sessions")
print("[auth] no-token ->", code, "(want 401)")

# 2. 错误密码 -> 401；正确密码 -> 拿 token
code, r = call("POST", "/api/auth/login", {"username": "admin", "password": "wrong"})
print("[auth] wrong-password ->", code, "(want 401)")
code, r = call("POST", "/api/auth/login", {"username": "admin", "password": "admin123"})
TOKEN = r["data"]["token"]
print("[auth] login ->", code, "user =", r["data"]["username"])

# 3. 业务数据 CRUD
code, r = call("GET", "/api/orders", token=TOKEN)
print("[orders] list ->", code, "count =", len(r))
code, r = call("POST", "/api/orders",
               {"order_id": "DD99990001", "status": "已发货", "amount": "66.00",
                "receiver": "测试员", "logistics": "测试物流"}, token=TOKEN)
print("[orders] create ->", code, r["data"])
code, r = call("POST", "/api/orders",
               {"order_id": "DD99990001", "status": "已签收", "amount": "66.00",
                "receiver": "测试员", "logistics": "已签收"}, token=TOKEN)
print("[orders] update ->", code, "(upsert)")
code, r = call("DELETE", "/api/orders/DD99990001", token=TOKEN)
print("[orders] delete ->", code)

code, r = call("GET", "/api/coupons", token=TOKEN)
print("[coupons] list ->", code, "count =", len(r))

# 4. 知识库 CRUD
code, r = call("POST", "/api/knowledge",
               {"question": "测试问题：门店地址在哪？", "answer": "测试答案：太原市迎泽区。",
                "keywords": "地址,门店,在哪"}, token=TOKEN)
KID = r["data"]["id"]
print("[knowledge] create ->", code, "id =", KID)
code, r = call("PUT", f"/api/knowledge/{KID}",
               {"question": "测试问题：门店地址在哪？", "answer": "修改后的答案。",
                "keywords": "地址,门店"}, token=TOKEN)
print("[knowledge] update ->", code)
code, r = call("GET", "/api/knowledge", token=TOKEN)
print("[knowledge] list ->", code, "count =", len(r))
code, r = call("DELETE", f"/api/knowledge/{KID}", token=TOKEN)
print("[knowledge] delete ->", code)

# 5. 智能体走真实库：改订单状态后提问，回答应包含新状态
call("POST", "/api/orders",
     {"order_id": "DD20240001", "status": "打包中", "amount": "199.00",
      "receiver": "张先生", "logistics": "预计今晚 22:00 前发出"}, token=TOKEN)
code, r = call("POST", "/api/agent/chat",
               {"message": "订单 DD20240001 现在什么状态？", "session_id": "smoke-db1"},
               token=TOKEN)
print("[agent/db-order] tools =", r["data"]["tools_used"], "|", r["data"]["reply"][:50])

# 6. 知识库工具
code, r = call("POST", "/api/agent/chat",
               {"message": "你们的退货政策是什么？", "session_id": "smoke-db1"}, token=TOKEN)
print("[agent/knowledge] tools =", r["data"]["tools_used"], "|", r["data"]["reply"][:60])

# 7. 统计埋点
code, r = call("GET", "/api/stats/overview", token=TOKEN)
print("[stats] sessions =", r["total_sessions"], "messages =", r["total_messages"],
      "tool_calls =", r["tool_calls_total"], "avg_ms =", r["avg_duration_ms"])
print("[stats] route_counter =", r["route_counter"], "tools =", list(r["tool_counter"].items())[:6])
