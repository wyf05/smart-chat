# -*- coding: utf-8 -*-
"""接口自动化冒烟测试：python test_api.py（需后端已启动在 8000 端口）
v3 起所有 /api 接口需要 JWT 登录（默认账号 admin / admin123）。"""
import json
import urllib.request

BASE = "http://127.0.0.1:8000"


def login() -> str:
    req = urllib.request.Request(
        BASE + "/api/auth/login",
        data=json.dumps({"username": "admin", "password": "admin123"}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["data"]["token"]


TOKEN = login()


def call(method: str, path: str, body: dict | None = None, raw: bool = False):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = resp.read().decode("utf-8")
        return payload if raw else json.loads(payload)


# 0. 会话需先存在（模拟前端行为：先建会话再对话）
r = call("POST", "/api/sessions")
SID = r["id"]

# 1. 智能体：订单查询
r = call("POST", "/api/agent/chat", {"message": "订单 DD20240001 到哪了？", "session_id": SID})
print("[agent/order]", r["data"]["tools_used"], "|", r["data"]["reply"][:60])

# 2. 智能体：自定义优惠券工具
r = call("POST", "/api/agent/chat", {"message": "优惠券 QUAN100 还能用吗？", "session_id": SID})
print("[agent/coupon]", r["data"]["tools_used"], "|", r["data"]["reply"][:60])

# 3. 意图路由
for msg in ("用一句话介绍 Docker", "帮我算 123*456", "写一首关于春天的诗", "订单 DD20240002 什么状态"):
    r = call("POST", "/api/smart/chat", {"message": msg, "session_id": SID})
    print("[smart]", r["data"]["route"], "<-", msg)

# 4. SSE 流式
req = urllib.request.Request(
    BASE + "/api/chat/stream",
    data=json.dumps({"message": "用二十个字介绍大海", "session_id": SID}).encode(),
    headers={"Content-Type": "application/json",
             "Authorization": f"Bearer {TOKEN}"}, method="POST")
with urllib.request.urlopen(req, timeout=120) as resp:
    chunks = resp.read().decode("utf-8")
    lines = [l for l in chunks.split("\n\n") if l.startswith("data: ")]
    text = "".join(json.loads(l[6:]).get("delta", "") for l in lines if l[6:] != "[DONE]")
    print("[stream] chunks =", len(lines), "|", text[:80])

# 5. 参数校验 422
try:
    call("POST", "/api/chat", {"message": "", "session_id": "x"})
    print("[validation] FAIL: no 422")
except urllib.error.HTTPError as e:
    print("[validation]", e.code, "OK" if e.code == 422 else "UNEXPECTED")

# 6. 统计埋点（本轮对话应已计入）
r = call("GET", "/api/stats/overview")
print("[stats] sessions =", r["total_sessions"], "tool_calls =", r["tool_calls_total"],
      "route =", r["route_counter"])
