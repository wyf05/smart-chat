"""认证与安全：密码哈希 + JWT 签发/校验 + FastAPI 依赖"""
import hashlib
import time

import jwt
from fastapi import Header, HTTPException

from app.config import JWT_SECRET

_SALT = "smart-chat"
_TOKEN_TTL = 12 * 3600   # token 有效期 12 小时


def hash_password(password: str) -> str:
    """加盐 sha256：demo 环境够用，生产应换 bcrypt/argon2"""
    return hashlib.sha256((_SALT + password).encode()).hexdigest()


def create_token(username: str) -> str:
    """签发 JWT：sub 存用户名，exp 存过期时间戳"""
    payload = {"sub": username, "exp": int(time.time()) + _TOKEN_TTL}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(authorization: str = Header(default="")) -> str:
    """FastAPI 依赖：校验 Authorization: Bearer <token>，返回用户名"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或 token 缺失")
    token = authorization[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效 token")
    return payload.get("sub", "")
