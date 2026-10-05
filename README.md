# 店小智 · 智能客服助手（SmartChat）

基于 **LangChain + FastAPI + Vue3 + Docker** 的企业级电商智能客服系统。

> 软件工程综合实践（企业级软件实践与工程能力提升训练营）课程项目 · 王一帆 · 软件2306

## 功能总览

| 模块 | 说明 |
| --- | --- |
| 多轮对话 | `/api/chat`，历史消息落库 SQLite，服务重启不丢；支持 SSE 流式打字机输出 |
| 智能体 | `/api/agent/chat`，ReAct 循环 + Function Calling，5 个业务工具，SqliteSaver 记忆持久化 |
| 统一入口（意图路由） | `/api/smart/chat`，结构化输出意图分类，自动分流"闲聊 / 需工具"链路 |
| 会话管理 | 列表 / 新建 / 删除 / 改名（PATCH）/ 历史消息，第一条消息自动生成会话标题 |
| 企业级特性 | 统一响应格式、滑动窗口限流（每 IP 每分钟 20 次）、全链路日志、异常兜底、密钥环境变量管理 |
| 交付 | `docker compose up -d --build` 一键部署，数据卷持久化，Nginx 反向代理 |

## 业务工具（智能体可调用）

| 工具 | 功能 |
| --- | --- |
| `query_order` | 订单物流状态查询（模拟数据，接口可替换真实订单系统） |
| `get_weather` | 城市天气查询（适合发货/出行判断） |
| `calculate` | 数学表达式精确计算（含非法字符过滤，防代码注入） |
| `get_current_time` | 当前日期时间 |
| `get_coupon` | 优惠券状态查询（自定义扩展工具） |

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
│   │   ├── main.py        # FastAPI 入口：中间件（日志+限流）+ 全部接口
│   │   ├── config.py      # 配置中心（.env 读取，密钥不入库）
│   │   ├── database.py    # SQLAlchemy 引擎/会话工厂
│   │   ├── models.py      # ORM：chat_sessions / chat_messages
│   │   ├── schemas.py     # Pydantic 请求/响应/意图模型
│   │   ├── llm.py         # 模型封装：chat() / classify_intent() / 流式
│   │   ├── memory.py      # 会话与消息的业务存取
│   │   └── agent.py       # 智能体：5 工具 + create_agent + SqliteSaver
│   ├── test_agent.py / test_eval.py / test_api.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue                # 布局与会话状态中枢
│   │   ├── api/index.js           # 接口层（唯一 axios 出口）
│   │   └── components/
│   │       ├── SessionSidebar.vue # 会话侧边栏
│   │       └── ChatPanel.vue      # 聊天面板（流式/智能体开关）
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
