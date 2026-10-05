"""配置中心：从 .env 文件读取全部配置（企业规范：配置集中一处管理，禁止散落各文件）"""
import os

from dotenv import load_dotenv

load_dotenv()   # 读取 backend/.env，把配置装进环境变量

API_KEY: str = os.getenv("LLM_API_KEY", "")
BASE_URL: str = os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
MODEL: str = os.getenv("LLM_MODEL", "glm-4-flash")
# 智能体单独用一个小模型：glm-4-flash 工具链路正常但多轮记忆召回弱，
# glm-4.5-flash（同免费）在"查完订单再追问订单号"类问题上召回正确
AGENT_MODEL: str = os.getenv("AGENT_MODEL", "glm-4.5-flash")
# 意图分类器单独用一个小模型：分类是指令遵循任务，glm-4-flash 会"顺手答题"导致分类失败
ROUTER_MODEL: str = os.getenv("ROUTER_MODEL", "glm-4.5-flash")
DB_PATH: str = os.getenv("DB_PATH", "data/smartchat.db")
AGENT_DB_PATH: str = os.getenv("AGENT_DB_PATH", "data/agent_memory.db")

# 限流阈值也是配置，集中在配置中心管理
RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", "20"))

# JWT 签名密钥：生产环境应通过环境变量注入随机长串
JWT_SECRET: str = os.getenv("JWT_SECRET", "smart-chat-dev-secret-change-me")

# 系统提示词：给 AI 定人设（电商客服场景）
SYSTEM_PROMPT: str = (
    "你是「店小智」，一家电商公司的智能客服。"
    "回答使用简体中文，礼貌、简洁、条理清晰。"
    "不确定的内容明确告知用户，绝不编造。"
)

if not API_KEY:
    raise RuntimeError("未找到 LLM_API_KEY，请检查 backend/.env 是否配置正确")
