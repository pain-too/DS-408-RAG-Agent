import streamlit as st
import os

# ==================== 兼容本地和云端的 API Key 读取 ====================
try:
    dashscope_key = st.secrets["DASHSCOPE_API_KEY"]
except (FileNotFoundError, KeyError, AttributeError):
    dashscope_key = os.environ.get("DASHSCOPE_API_KEY")

if not dashscope_key:
    st.error("❌ 未找到 DASHSCOPE_API_KEY，请在 Streamlit Secrets 或环境变量中设置")
    st.stop()

os.environ["DASHSCOPE_API_KEY"] = dashscope_key

# ==================== 延迟导入：确保 API Key 已设置 ====================
# 不要在这里导入！让后面的函数内部导入

st.set_page_config(page_title="408答疑助手", page_icon="📚")
st.title("📚 DS-408-RAG-Agent 考研智能答疑")

# ==================== 初始化 RAG 和 Agent（延迟初始化）====================
@st.cache_resource
def init_services():
    # 在函数内部导入，确保 API Key 已经设置
    from rag.ds_rag_service import DSRagService
    from react_agent import ReactAgent
    
    rag = DSRagService(data_path=None)  # 不自动加载 PDF
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
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent 正在思考..."):
            full_answer = ""
            placeholder = st.empty()
            
            for chunk in agent.execute_stream(prompt):
                full_answer += chunk
                placeholder.markdown(full_answer)

    st.session_state.messages.append({"role": "assistant", "content": full_answer})
