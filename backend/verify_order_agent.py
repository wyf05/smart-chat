# -*- coding: utf-8 -*-
"""验证智能体 query_order 读取新订单数据"""
import json
import urllib.request

BASE = "http://127.0.0.1:8000"

def post(path, payload, token=None):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)

login = post("/api/auth/login", {"username": "admin", "password": "admin123"})
token = login["data"]["token"]
res = post("/api/agent/chat",
           {"message": "王一帆的订单 DD20260005 现在到哪了？", "session_id": "verify-2026"},
           token)
d = res["data"]
print("tools:", d["tools_used"])
print("reply:", d["reply"][:200])
