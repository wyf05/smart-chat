"""数据库连接：SQLAlchemy 引擎 + 会话工厂 + 建表/迁移/种子数据入口"""
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DB_PATH

# 确保 data 目录存在（SQLite 的库文件放在这里）
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# check_same_thread=False 允许多线程访问（Web 服务必需）
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

# SessionLocal：数据库会话工厂，用完必须 close（相当于一次数据库连接）
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# Base：所有 ORM 模型的父类
Base = declarative_base()

# 轻量迁移：老库升级时补充新增列（已存在则忽略报错）
_MIGRATIONS = [
    "ALTER TABLE chat_messages ADD COLUMN route VARCHAR",
    "ALTER TABLE chat_messages ADD COLUMN tools_used VARCHAR",
    "ALTER TABLE chat_messages ADD COLUMN duration_ms INTEGER",
]


def _seed(db) -> None:
    """首次启动写入演示种子数据（订单/优惠券/知识库/管理员账号）"""
    from app.models import Coupon, KnowledgeItem, Order, User
    import hashlib

    if db.query(Order).count() == 0:
        db.add_all([
            Order(order_id="DD20240001", status="已发货", amount="199.00",
                  receiver="张先生", logistics="顺丰速运，预计明天 18:00 前送达"),
            Order(order_id="DD20240002", status="待付款", amount="129.00",
                  receiver="李女士", logistics="30 分钟内未支付将自动取消"),
            Order(order_id="DD20240003", status="已签收", amount="89.00",
                  receiver="王先生", logistics="2026-09-18 14:32 签收"),
            Order(order_id="DD20240004", status="打包中", amount="259.00",
                  receiver="赵女士", logistics="预计今天 20:00 前发出"),
        ])
    if db.query(Coupon).count() == 0:
        db.add_all([
            Coupon(code="QUAN100", title="满100减20券", discount="满 100 元减 20 元",
                   valid_until="2026-10-31", status="可用"),
            Coupon(code="QUAN50", title="满50减10券", discount="满 50 元减 10 元",
                   valid_until="2026-09-30", status="已过期"),
            Coupon(code="QUANNEW", title="新人立减15券", discount="无门槛立减 15 元",
                   valid_until="2026-12-31", status="已使用"),
            Coupon(code="QUANVIP", title="会员9折券", discount="会员专享 9 折",
                   valid_until="2026-12-31", status="可用"),
        ])
    if db.query(KnowledgeItem).count() == 0:
        db.add_all([
            KnowledgeItem(question="退货政策是什么？",
                          answer="自签收之日起 7 天内支持无理由退货，商品需保持完好；"
                                 "质量问题 15 天内可退换，运费由商家承担。",
                          keywords="退货,退款,退换,售后"),
            KnowledgeItem(question="发货时间是几点？",
                          answer="每天 16:00 前下单的订单当天发货，16:00 后的订单次日发货；"
                                 "法定节假日顺延。",
                          keywords="发货,发货时间,多久发货,物流"),
            KnowledgeItem(question="支持哪些付款方式？",
                          answer="支持微信支付、支付宝、银联卡以及平台余额支付；"
                                 "大额订单支持花呗分期。",
                          keywords="付款,支付,微信,支付宝,分期"),
            KnowledgeItem(question="如何开发票？",
                          answer="订单完成后可在“订单详情-申请开票”中申请电子发票，"
                                 "支持普票与专票，1-3 个工作日内开具。",
                          keywords="发票,开票,报销"),
        ])
    if db.query(User).count() == 0:
        salt = "smart-chat"
        db.add(User(username="admin",
                    password_hash=hashlib.sha256((salt + "admin123").encode()).hexdigest()))
    db.commit()


def init_db() -> None:
    """建表 → 补列（老库迁移）→ 种子数据（已有表则跳过）"""
    from app import models   # 延迟导入：确保模型定义先被加载
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        for stmt in _MIGRATIONS:
            try:
                conn.execute(text(stmt))
            except Exception:
                pass   # 列已存在，忽略
    db = SessionLocal()
    try:
        _seed(db)
    finally:
        db.close()
