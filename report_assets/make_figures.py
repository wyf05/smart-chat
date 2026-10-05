# -*- coding: utf-8 -*-
"""生成报告用图：系统架构图、功能模块图、部署架构图（matplotlib 绘制）"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

OUT = r"D:\smart-chat\report_assets"


def box(ax, x, y, w, h, text, fc="#e8f1fb", ec="#2b6cb0", fs=11, bold=False):
    r = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                fc=fc, ec=ec, lw=1.4)
    ax.add_patch(r)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, fontweight="bold" if bold else "normal")


def arrow(ax, x1, y1, x2, y2, text="", style="-|>", color="#444444"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=1.4))
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.015, text, ha="center",
                fontsize=9, color="#333333")


# ================= 图1 系统总体架构图 =================
fig, ax = plt.subplots(figsize=(9.2, 7.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

# 前端层
ax.text(5, 9.7, "店小智 · 智能客服系统总体架构", ha="center", fontsize=14, fontweight="bold")
ax.add_patch(mpatches.FancyBboxPatch((0.4, 7.9), 9.2, 1.4, boxstyle="round,pad=0.03", fc="#f0f7ff", ec="#2b6cb0", lw=1.6))
ax.text(0.75, 8.95, "前端层（Vue3 + Element Plus，浏览器 :5173 / Nginx :8080）", fontsize=10.5, fontweight="bold")
box(ax, 0.8, 8.05, 2.4, 0.62, "SessionSidebar\n会话侧边栏", fs=9.5)
box(ax, 3.5, 8.05, 2.8, 0.62, "ChatPanel\n聊天面板/开关", fs=9.5)
box(ax, 6.6, 8.05, 2.9, 0.62, "api/index.js\nAxios 接口层", fs=9.5)

arrow(ax, 5, 7.85, 5, 7.15, "HTTP /api（Vite 代理 / Nginx 反向代理）")

# 后端层
ax.add_patch(mpatches.FancyBboxPatch((0.4, 3.55), 9.2, 3.5, boxstyle="round,pad=0.03", fc="#f7fbf3", ec="#388e3c", lw=1.6))
ax.text(0.75, 6.7, "后端层（FastAPI，:8000，分层架构）", fontsize=10.5, fontweight="bold")
box(ax, 0.8, 5.85, 3.8, 0.62, "main.py 路由层\n日志/限流中间件 · 统一响应", fs=9.5)
box(ax, 5.0, 5.85, 4.2, 0.62, "schemas.py\nPydantic 请求/响应/意图模型", fs=9.5)
box(ax, 0.8, 4.85, 3.8, 0.62, "llm.py 模型封装\nchat() · classify_intent()", fs=9.5)
box(ax, 5.0, 4.85, 4.2, 0.62, "agent.py 智能体\n5 工具 · ReAct · SqliteSaver 记忆", fs=9.5)
box(ax, 0.8, 3.85, 3.8, 0.62, "memory.py 业务层\n会话 CRUD · 历史消息", fs=9.5)
box(ax, 5.0, 3.85, 4.2, 0.62, "config.py 配置中心\n.env 密钥/模型/限流阈值", fs=9.5)

arrow(ax, 2.7, 3.5, 2.7, 2.8, "ORM（SQLAlchemy）")
arrow(ax, 7.1, 3.5, 7.1, 2.8, "OpenAI 兼容协议（HTTP）")
arrow(ax, 4.6, 5.0, 5.0, 5.0, "", color="#888888")

# 数据与模型层
ax.add_patch(mpatches.FancyBboxPatch((0.4, 0.5), 4.4, 2.1, boxstyle="round,pad=0.03", fc="#fffdf2", ec="#b8860b", lw=1.6))
ax.text(2.6, 2.28, "数据层（SQLite）", fontsize=10.5, fontweight="bold", ha="center")
box(ax, 0.8, 1.45, 3.6, 0.6, "chat_sessions / chat_messages\n业务库 smartchat.db", fs=8.8)
box(ax, 0.8, 0.7, 3.6, 0.6, "agent_memory.db\nLangGraph 检查点（智能体记忆）", fs=8.8)

ax.add_patch(mpatches.FancyBboxPatch((5.2, 0.5), 4.4, 2.1, boxstyle="round,pad=0.03", fc="#fdf3f7", ec="#c2185b", lw=1.6))
ax.text(7.4, 2.28, "大模型服务（智谱开放平台）", fontsize=10.5, fontweight="bold", ha="center")
box(ax, 5.6, 1.45, 3.6, 0.6, "glm-4-flash\n日常对话 / SSE 流式", fs=8.8)
box(ax, 5.6, 0.7, 3.6, 0.6, "glm-4.5-flash\n意图分类 / 智能体（工具调用）", fs=8.8)

plt.tight_layout()
plt.savefig(f"{OUT}/fig_arch.png", dpi=170, bbox_inches="tight")
plt.close()

# ================= 图2 功能模块图 =================
fig, ax = plt.subplots(figsize=(9.2, 5.6))
ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")
ax.text(5, 6.6, "功能模块划分", ha="center", fontsize=14, fontweight="bold")

box(ax, 3.4, 5.3, 3.2, 0.8, "店小智智能客服系统", fc="#2b6cb0", ec="#1a4a80", fs=12.5, bold=True)
ax.text(5, 5.3, "", ha="center")

mods = [
    (0.4, "多轮对话模块\n/api/chat\nSSE 流式输出"),
    (2.3, "智能体模块\n/api/agent/chat\n5 个业务工具\nReAct 循环"),
    (4.2, "统一入口路由\n/api/smart/chat\n意图识别分流\nchat / agent"),
    (6.1, "会话管理模块\n列表/新建/删除\n改名/历史消息"),
    (8.0, "基础设施\n限流 · 日志\nDocker 部署"),
]
for x, t in mods:
    box(ax, x, 2.6, 1.6, 1.9, t, fs=8.8)
    ax.plot([5, x + 0.8], [5.25, 4.55], color="#666666", lw=1.1)

ax.text(5, 1.7, "数据支撑：SQLite 业务库（会话/消息持久化） + agent_memory.db（智能体记忆） + 大模型 API（智谱）",
        ha="center", fontsize=9.5, color="#555555")
plt.tight_layout()
plt.savefig(f"{OUT}/fig_modules.png", dpi=170, bbox_inches="tight")
plt.close()

# ================= 图3 部署架构图 =================
fig, ax = plt.subplots(figsize=(9.2, 5.8))
ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")
ax.text(5, 6.6, "Docker Compose 部署架构", ha="center", fontsize=14, fontweight="bold")

ax.add_patch(mpatches.FancyBboxPatch((0.3, 0.4), 9.4, 5.7, boxstyle="round,pad=0.03",
                                     fc="#fcfcfc", ec="#888888", lw=1.2, linestyle="--"))
ax.text(5, 5.85, "宿主机（Docker Engine）", ha="center", fontsize=10.5, color="#555555")

# 用户
box(ax, 0.7, 3.9, 1.5, 0.9, "用户浏览器", fc="#e8f1fb", fs=10)

# frontend 容器
box(ax, 3.0, 3.5, 2.9, 1.7, "smart-chat-frontend\nNginx :80\n静态页面 + 反向代理\n（proxy_buffering off 支持 SSE）",
    fc="#f0f7ff", fs=8.8, bold=False)

# backend 容器
box(ax, 6.5, 3.5, 2.9, 1.7, "smart-chat-backend\nuvicorn :8000（仅容器网络内）\nFastAPI + 智能体\nenv_file 注入密钥",
    fc="#f7fbf3", fs=8.8)

# 数据卷
box(ax, 6.5, 1.0, 2.9, 1.4, "数据卷（Volume）\n宿主机 backend/data\nsmartchat.db / agent_memory.db\n容器删除数据不丢", fc="#fffdf2", fs=8.8)

# 外部服务
box(ax, 3.0, 1.0, 2.9, 1.4, "智谱开放平台\nopen.bigmodel.cn\nglm-4-flash / glm-4.5-flash\n（OpenAI 兼容协议）", fc="#fdf3f7", fs=8.8)

arrow(ax, 2.25, 4.35, 2.95, 4.35, "http://localhost:8080")
arrow(ax, 5.95, 4.35, 6.45, 4.35, "/api/ 反向代理")
arrow(ax, 7.95, 3.45, 7.95, 2.45, "挂载")
arrow(ax, 5.95, 2.0, 6.45, 1.7, "HTTPS")

plt.tight_layout()
plt.savefig(f"{OUT}/fig_deploy.png", dpi=170, bbox_inches="tight")
plt.close()

print("3 figures saved to", OUT)
