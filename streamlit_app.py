import streamlit as st
import os

# ==================== 兼容本地和云端的 API Key 读取 ====================
try:
    # Streamlit Cloud 环境
    dashscope_key = st.secrets["DASHSCOPE_API_KEY"]
except (FileNotFoundError, KeyError, AttributeError):
    # 本地开发环境
    dashscope_key = os.environ.get("DASHSCOPE_API_KEY")

if not dashscope_key:
    st.error("❌ 未找到 DASHSCOPE_API_KEY，请在 Streamlit Secrets 或环境变量中设置")
    st.stop()

os.environ["DASHSCOPE_API_KEY"] = dashscope_key

# ==================== 导入模块（放在 key 设置之后） ====================
from react_agent import ReactAgent
from rag.ds_rag_service import DSRagService

st.set_page_config(page_title="408答疑助手", page_icon="📚")
st.title("📚 DS-408-RAG-Agent 考研智能答疑")


# ==================== 初始化 RAG 和 Agent ====================
@st.cache_resource
def init_services():
    """缓存服务，避免重复初始化"""
    rag = DSRagService()
    agent = ReactAgent()
    return rag, agent


try:
    rag, agent = init_services()
    st.success("✅ 知识库加载成功")
except Exception as e:
    st.error(f"❌ 初始化失败: {e}")
    st.stop()

# ==================== 对话历史 ====================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==================== 用户输入 ====================
prompt = st.chat_input("请输入你的问题...")

if prompt:
    # 显示用户问题
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 回答（使用 Agent）
    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent 正在思考..."):
            full_answer = ""
            placeholder = st.empty()

            # Agent 流式执行
            for chunk in agent.execute_stream(prompt):
                full_answer += chunk
                placeholder.markdown(full_answer)

    # 保存历史
    st.session_state.messages.append({"role": "assistant", "content": full_answer})