# 店小智 · 智能客服助手（SmartChat）

基于 **LangChain + FastAPI + Vue3 + Docker** 的企业级电商智能客服系统。

> 软件工程综合实践（企业级软件实践与工程能力提升训练营）课程项目 · 王一帆 · 软件2306

## 功能总览

系统采用多页面工作台形态（登录 → 首页仪表盘 → 各子页面）：

| 页面 | 说明 |
| --- | --- |
| 登录页 | JWT 账号登录（默认演示账号 `admin / admin123`），所有接口持 token 访问 |
| 首页仪表盘 | 会话数/消息数/工具调用数/平均耗时指标卡 + 子页面入口 |
| 智能对话 | 多轮对话 + SQLite 持久化；SSE 流式打字机；智能体 6 工具；意图路由统一入口 |
| 业务数据中心 | 订单/优惠券的数据库化管理（增删改），一键"去咨询"联动智能体验证真实数据 |
| 智能知识库 | FAQ 维护（增删改查），检索封装为智能体第 6 个工具 `search_knowledge`，回答注明"来自知识库"；支持页内检索效果测试 |
| 数据统计 | 基于对话埋点的 ECharts 看板：工具调用分布、意图路由占比、近 7 日消息量、平均耗时 |

| 后端模块 | 说明 |
| --- | --- |
| 会话管理 | 列表 / 新建 / 删除 / 改名（PATCH）/ 历史消息，首条消息自动生成会话标题 |
| 企业级特性 | JWT 鉴权、统一响应格式、滑动窗口限流（每 IP 每分钟 20 次）、全链路日志、异常兜底、密钥环境变量管理 |
| 统计埋点 | 每轮对话记录 route（chat/agent）、tools_used、duration_ms，支撑数据统计页 |
| 交付 | `docker compose up -d --build` 一键部署，数据卷持久化，Nginx 反向代理 |

## 业务工具（智能体可调用）

| 工具 | 功能 |
| --- | --- |
| `query_order` | 订单状态查询（**读业务数据库 orders 表**，后台改数据回答实时变） |
| `get_weather` | 城市天气查询（适合发货/出行判断） |
| `calculate` | 数学表达式精确计算（含非法字符过滤，防代码注入） |
| `get_current_time` | 当前日期时间 |
| `get_coupon` | 优惠券状态查询（**读业务数据库 coupons 表**） |
| `search_knowledge` | 知识库检索（**读 knowledge_items 表**，评分细则点名的创新加分项） |

## 技术栈

- **后端**：Python 3.11+ / FastAPI / SQLAlchemy(ORM) / SQLite / LangChain 1.x + LangGraph
- **前端**：Vue3 / Element Plus / Vite / Axios
- **大模型**：智谱开放平台（OpenAI 兼容协议，`glm-4-flash` 对话、`glm-4.5-flash` 意图分类与智能体）
- **部署**：Docker 多阶段构建 / Nginx 反向代理 / Docker Compose 数据卷

## 快速开始

### 0. 准备

- Python 3.11+、Node.js 18+、Docker Desktop
- 大模型 API Key（智谱 [bigmodel.cn](https://open.bigmodel.cn/)，或任何 OpenAI 兼容服务）

### 1. 配置密钥

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入你的 LLM_API_KEY
```

### 2. 本地开发运行

```bash
# 后端
cd backend
python -m venv ../.venv
../.venv/Scripts/pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
../.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
# 接口文档：http://127.0.0.1:8000/docs

# 前端（新开终端）
cd frontend
npm install
npm run dev
# 页面：http://localhost:5173
```

### 3. Docker 一键部署

```bash
docker compose up -d --build
# 访问：http://localhost:8080
# 毁灭测试：docker compose down && docker compose up -d，历史会话仍在（数据卷生效）
```

## 测试与评估

```bash
cd backend
python test_agent.py   # 智能体五工具 + 记忆召回验证
python test_eval.py    # 工具选择正确率评估（12 用例，实测 12/12 = 100%）
python test_api.py     # 接口冒烟测试（需后端已启动）
```

## 项目结构

```
smart-chat/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI 入口：认证 + 中间件（日志+限流）+ 全部接口
│   │   ├── config.py      # 配置中心（.env 读取，密钥不入库）
│   │   ├── database.py    # 引擎/建表/轻量迁移/种子数据
│   │   ├── models.py      # ORM：会话/消息(含埋点)/订单/优惠券/知识库/用户
│   │   ├── schemas.py     # Pydantic 请求/响应/意图模型
│   │   ├── security.py    # JWT 签发校验 + 密码哈希
│   │   ├── catalog.py     # 业务数据中心：订单/优惠券/知识库存取与检索
│   │   ├── stats.py       # 统计聚合（数据统计页数据源）
│   │   ├── llm.py         # 模型封装：chat() / classify_intent() / 流式
│   │   ├── memory.py      # 会话与消息的业务存取（含统计埋点）
│   │   └── agent.py       # 智能体：6 工具 + create_agent + SqliteSaver
│   ├── test_agent.py / test_eval.py / test_api.py / test_v3.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── router/index.js        # 路由 + 登录守卫
│   │   ├── layouts/AppLayout.vue  # 顶部导航布局
│   │   ├── api/index.js           # 接口层（axios + JWT 拦截器）
│   │   ├── views/
│   │   │   ├── LoginView.vue      # 登录页
│   │   │   ├── DashboardView.vue  # 首页仪表盘
│   │   │   ├── ChatView.vue       # 智能对话
│   │   │   ├── DataCenterView.vue # 业务数据中心（订单/优惠券）
│   │   │   ├── KnowledgeView.vue  # 智能知识库
│   │   │   └── StatsView.vue      # 数据统计（ECharts）
│   │   └── components/            # SessionSidebar / ChatPanel
│   ├── Dockerfile / nginx.conf    # 多阶段构建 + 反向代理
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 关键设计

1. **双库分离**：业务库（会话/消息，给前端展示）与智能体检查点库（给模型的多轮状态）各司其职；
2. **意图路由**：闲聊走普通链路（1 次模型调用），业务问题走智能体链路（多次工具往返），兼顾成本与体验；
3. **模型分工**：`glm-4-flash` 做日常对话（快），`glm-4.5-flash` 做意图分类与智能体（工具调用与多轮召回更稳），均免费；
4. **安全**：API Key 只经 `.env` / compose `env_file` 注入、计算工具白名单过滤防注入、限流防刷、异常统一兜底不暴露堆栈。

## License

仅用于课程学习交流。
