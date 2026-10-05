"""统计聚合：数据统计页的数据源（从 chat_messages 埋点字段聚合）"""
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ChatMessage, ChatSession


def overview(db: Session) -> dict:
    """首页仪表盘 + 统计页共用的聚合数据"""
    total_sessions = db.scalar(select(func.count()).select_from(ChatSession)) or 0
    total_messages = db.scalar(
        select(func.count()).select_from(ChatMessage).where(ChatMessage.role == "user")) or 0

    # 埋点行（assistant 行且 route 非空）
    rows = db.scalars(
        select(ChatMessage).where(ChatMessage.role == "assistant", ChatMessage.route.is_not(None))
    ).all()

    tool_counter: dict[str, int] = {}
    route_counter = {"chat": 0, "agent": 0}
    durations = []
    for r in rows:
        route_counter[r.route] = route_counter.get(r.route, 0) + 1
        if r.tools_used:
            for t in r.tools_used.split(","):
                t = t.strip()
                if t:
                    tool_counter[t] = tool_counter.get(t, 0) + 1
        if r.duration_ms:
            durations.append(r.duration_ms)

    tool_calls_total = sum(tool_counter.values())
    avg_ms = int(sum(durations) / len(durations)) if durations else 0

    # 近 7 天每日用户消息量
    days, counts = [], []
    today = datetime.now().date()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        start = datetime.combine(day, datetime.min.time())
        end = start + timedelta(days=1)
        c = db.scalar(
            select(func.count()).select_from(ChatMessage).where(
                ChatMessage.role == "user",
                ChatMessage.created_at >= start,
                ChatMessage.created_at < end,
            )) or 0
        days.append(day.strftime("%m-%d"))
        counts.append(c)

    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "tool_calls_total": tool_calls_total,
        "avg_duration_ms": avg_ms,
        "route_counter": route_counter,
        "tool_counter": dict(sorted(tool_counter.items(), key=lambda x: -x[1])),
        "daily": {"days": days, "counts": counts},
    }
