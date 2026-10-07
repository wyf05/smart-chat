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


class LoginRequest(BaseModel):
    """登录请求体"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)


class RegisterRequest(BaseModel):
    """注册请求体：用户名 3-20 位字母/数字/下划线，密码至少 6 位"""
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^[A-Za-z0-9_]+$",
                          description="用户名：3-20 位字母/数字/下划线")
    password: str = Field(..., min_length=6, max_length=100, description="密码：至少 6 位")


class OrderIn(BaseModel):
    """订单新增/修改请求体"""
    order_id: str = Field(..., min_length=1, max_length=32, description="订单号")
    status: str = Field(..., description="状态：待付款/打包中/已发货/已签收")
    amount: str = Field(..., description="订单金额")
    receiver: str = Field(..., max_length=50, description="收件人")
    logistics: str | None = Field(None, max_length=200, description="物流信息")


class CouponIn(BaseModel):
    """优惠券新增/修改请求体"""
    code: str = Field(..., min_length=1, max_length=32, description="券码")
    title: str = Field(..., min_length=1, max_length=50, description="券名称")
    discount: str = Field(..., max_length=100, description="优惠说明")
    valid_until: str | None = Field(None, max_length=20, description="有效期至")
    status: str = Field(..., description="状态：可用/已使用/已过期")


class KnowledgeIn(BaseModel):
    """知识库条目新增/修改请求体"""
    question: str = Field(..., min_length=1, max_length=200, description="问题")
    answer: str = Field(..., min_length=1, description="标准答案")
    keywords: str | None = Field(None, max_length=200, description="检索关键词，逗号分隔")


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
