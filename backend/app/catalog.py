"""业务数据中心：订单/优惠券/知识库的存取规则（智能体工具的数据源）"""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Coupon, KnowledgeItem, Order


# ---------------- 订单 ----------------
def list_orders(db: Session) -> list[Order]:
    return list(db.scalars(select(Order).order_by(Order.order_id)))


def upsert_order(db: Session, order_id: str, status: str, amount: str,
                 receiver: str, logistics: str | None = None) -> Order:
    """新增或更新订单（业务数据中心保存时调用）"""
    order = db.get(Order, order_id)
    if not order:
        order = Order(order_id=order_id)
        db.add(order)
    order.status, order.amount = status, amount
    order.receiver, order.logistics = receiver, logistics
    db.commit()
    return order


def delete_order(db: Session, order_id: str) -> bool:
    order = db.get(Order, order_id)
    if not order:
        return False
    db.delete(order)
    db.commit()
    return True


def query_order_by_id(db: Session, order_id: str) -> str:
    """供智能体 query_order 工具调用：返回自然语言描述"""
    order = db.get(Order, order_id.strip().upper())
    if not order:
        return f"未找到订单 {order_id}，请核对订单号（示例：DD20260001）"
    parts = [f"订单 {order.order_id} 状态：{order.status}，金额 {order.amount} 元，收件人 {order.receiver}"]
    if order.logistics:
        parts.append(f"物流信息：{order.logistics}")
    return "；".join(parts)


# ---------------- 优惠券 ----------------
def list_coupons(db: Session) -> list[Coupon]:
    return list(db.scalars(select(Coupon).order_by(Coupon.code)))


def upsert_coupon(db: Session, code: str, title: str, discount: str,
                  valid_until: str | None, status: str) -> Coupon:
    coupon = db.get(Coupon, code)
    if not coupon:
        coupon = Coupon(code=code)
        db.add(coupon)
    coupon.title, coupon.discount = title, discount
    coupon.valid_until, coupon.status = valid_until, status
    db.commit()
    return coupon


def delete_coupon(db: Session, code: str) -> bool:
    coupon = db.get(Coupon, code)
    if not coupon:
        return False
    db.delete(coupon)
    db.commit()
    return True


def query_coupon_by_code(db: Session, code: str) -> str:
    """供智能体 get_coupon 工具调用"""
    coupon = db.get(Coupon, code.strip().upper())
    if not coupon:
        return f"未找到优惠券 {code}，请核对券码（示例：QUAN100）"
    return (f"优惠券 {coupon.code}：{coupon.title}，{coupon.discount}，"
            f"有效期至 {coupon.valid_until or '长期'}，当前状态：{coupon.status}")


# ---------------- 知识库 ----------------
def list_knowledge(db: Session) -> list[KnowledgeItem]:
    return list(db.scalars(select(KnowledgeItem).order_by(KnowledgeItem.id)))


def add_knowledge(db: Session, question: str, answer: str, keywords: str | None) -> KnowledgeItem:
    item = KnowledgeItem(question=question, answer=answer, keywords=keywords or "")
    db.add(item)
    db.commit()
    return item


def update_knowledge(db: Session, item_id: int, question: str, answer: str,
                     keywords: str | None) -> bool:
    item = db.get(KnowledgeItem, item_id)
    if not item:
        return False
    item.question, item.answer, item.keywords = question, answer, keywords or ""
    db.commit()
    return True


def delete_knowledge(db: Session, item_id: int) -> bool:
    item = db.get(KnowledgeItem, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def search_knowledge(db: Session, query: str, top_k: int = 1) -> list[KnowledgeItem]:
    """轻量检索：关键词重合度打分（问答词命中数 + LIKE 兜底）。

    教学场景够用；数据量大后可平滑替换为向量检索（嵌入 + 余弦相似度）。
    """
    items = db.scalars(select(KnowledgeItem)).all()
    if not items:
        return []
    q = query.strip()
    scored = []
    for item in items:
        kws = [k.strip() for k in (item.keywords or "").split(",") if k.strip()]
        score = sum(1 for k in kws if k and k in q)
        # 兜底：问题文本直接出现在 query 中，或 query 的片段出现在问题里
        if item.question and (item.question in q or q in item.question):
            score += 2
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        # LIKE 兜底：任一词条模糊命中
        like = f"%{q[:10]}%"
        fuzzy = db.scalars(
            select(KnowledgeItem).where(or_(
                KnowledgeItem.question.like(like),
                KnowledgeItem.keywords.like(f"%{q[:4]}%"),
            ))
        ).all()
        return list(fuzzy)[:top_k]
    return [item for _, item in scored[:top_k]]
