"""请求与响应的数据模型：接口的"合同"，前后端都照此开发"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    """对话请求体"""
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    session_id: str = Field(..., description="会话ID")


class ChatResponse(BaseModel):
    """统一响应体：code=0 成功，非 0 失败"""
    code: int = 0
    message: str = "success"
    data: dict = {}


class SessionTitleUpdate(BaseModel):
    """会话标题修改请求体"""
    title: str = Field(..., min_length=1, max_length=50, description="新标题")


class Intent(BaseModel):
    """意图分类结果（供 /api/smart/chat 意图路由使用）"""
    intent: Literal["chat", "agent"] = Field(
        description="chat=日常问答闲聊；agent=需要订单/天气/时间/计算/优惠券等工具的请求"
    )

    @field_validator("intent", mode="before")
    @classmethod
    def _normalize(cls, v):
        """容错处理：模型偶尔返回 'Chat'/'agent。' 等带大小写或标点的值，统一归一化"""
        s = str(v).strip().lower()
        return "agent" if "agent" in s else "chat"


class SessionOut(BaseModel):
    """会话信息（返回给前端的格式）"""
    model_config = ConfigDict(from_attributes=True)   # 允许直接从 ORM 对象转换

    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    """消息内容（返回给前端的格式）"""
    model_config = ConfigDict(from_attributes=True)

    role: str
    content: str
    created_at: datetime
