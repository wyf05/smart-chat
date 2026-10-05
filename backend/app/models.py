"""ORM 数据表模型：类 = 表，属性 = 列"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ChatSession(Base):
    """会话表：一次连续对话的元信息"""
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)                       # 会话ID（uuid 字符串）
    title = Column(String, default="新对话", nullable=False)    # 会话标题
    created_at = Column(DateTime, default=datetime.now)         # 创建时间
    updated_at = Column(DateTime, default=datetime.now,
                        onupdate=datetime.now)                  # 最近活跃时间，自动更新

    # 关系：删除会话时级联删除其全部消息
    messages = relationship("ChatMessage", back_populates="session",
                            cascade="all, delete-orphan")


class ChatMessage(Base):
    """消息表：一条一条的对话记录（含统计埋点字段，供数据统计页分析）"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role = Column(String, nullable=False)       # "user" 或 "assistant"
    content = Column(Text, nullable=False)      # 消息内容
    created_at = Column(DateTime, default=datetime.now)
    # ===== 统计埋点：本轮走哪条链路、调用了哪些工具、耗时多少毫秒 =====
    route = Column(String, nullable=True)           # chat / agent / smart，None 表示流式等旧数据
    tools_used = Column(String, nullable=True)      # 逗号分隔的工具名，如 "query_order,calculate"
    duration_ms = Column(Integer, nullable=True)    # 本轮对话总耗时（毫秒）

    session = relationship("ChatSession", back_populates="messages")


class Order(Base):
    """订单表：业务数据中心管理，智能体 query_order 工具查询的数据源"""
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True)     # 订单号，如 DD20240001
    status = Column(String, nullable=False, default="待付款")   # 待付款/打包中/已发货/已签收
    amount = Column(String, nullable=False, default="0.00")     # 订单金额
    receiver = Column(String, nullable=False, default="")       # 收件人
    logistics = Column(String, nullable=True)                   # 物流公司与预计送达
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Coupon(Base):
    """优惠券表：业务数据中心管理，智能体 get_coupon 工具查询的数据源"""
    __tablename__ = "coupons"

    code = Column(String, primary_key=True)         # 券码，如 QUAN100
    title = Column(String, nullable=False)          # 券名称，如 满100减20券
    discount = Column(String, nullable=False, default="")       # 优惠说明
    valid_until = Column(String, nullable=True)     # 有效期至
    status = Column(String, nullable=False, default="可用")     # 可用/已使用/已过期
    created_at = Column(DateTime, default=datetime.now)


class KnowledgeItem(Base):
    """知识库条目：FAQ 管理，智能体 search_knowledge 工具检索的数据源"""
    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String, nullable=False)       # 问题（标题）
    answer = Column(Text, nullable=False)           # 标准答案
    keywords = Column(String, nullable=True)        # 检索关键词，逗号分隔
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class User(Base):
    """用户表：JWT 登录鉴权"""
    __tablename__ = "users"

    username = Column(String, primary_key=True)
    password_hash = Column(String, nullable=False)  # sha256(salt + password)
    role = Column(String, nullable=False, default="admin")
    created_at = Column(DateTime, default=datetime.now)
