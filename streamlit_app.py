import streamlit as st
import os

# ==================== 兼容本地 & 云端环境的 API Key 加载 ====================
try:
    # 优先从 Streamlit Cloud  Secrets 读取
    dashscope_key = st.secrets["DASHSCOPE_API_KEY"]
except (FileNotFoundError, KeyError, AttributeError):
    # 本地环境从系统变量读取
    dashscope_key = os.environ.get("DASHSCOPE_API_KEY")

if not dashscope_key:
    st.error("❌ 未找到 DASHSCOPE_API_KEY，请配置后重试")
    st.stop()

os.environ["DASHSCOPE_API_KEY"] = dashscope_key

# ==================== 页面基础配置 ====================
st.set_page_config(page_title="408答疑助手", page_icon="📚")
st.title("📚 DS-408-RAG-Agent 考研智能答疑")

# ==================== 核心服务延迟初始化（避免依赖加载顺序问题） ====================
@st.cache_resource
def init_services():
    """
    初始化 RAG 知识库 + Agent 智能体
    延迟导入：确保环境变量、密钥已完全配置
    """
    from rag.ds_rag_service import DSRagService
    from react_agent import ReactAgent

    rag = DSRagService(data_path=None)  # 不自动加载PDF
    agent = ReactAgent()
    return rag, agent

# 初始化并捕获全局异常
try:
    rag, agent = init_services()
    st.success("✅ 知识库加载成功 | Agent 准备就绪")
except Exception as e:
    st.error(f"❌ 初始化失败: {e}")
    st.stop()

# ==================== 对话历史管理 ====================
if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==================== 用户输入 ====================
prompt = st.chat_input("请输入你的 408 相关问题...")

if prompt:
    # 1. 把用户问题存入历史
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. AI 流式回答
    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent 思考中 · 工具调用中 · 生成答案中..."):
            full_answer = ""
            placeholder = st.empty()

            # 流式输出：支持思考 + 工具调用 + 最终回答
            for chunk in agent.execute_stream(prompt):
                full_answer += chunk
                placeholder.markdown(full_answer)

    # 3. 把 AI 回答存入历史
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_answer
    })