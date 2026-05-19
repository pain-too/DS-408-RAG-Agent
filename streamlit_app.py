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

# ==================== 页面基础配置 ====================
st.set_page_config(page_title="408答疑助手", page_icon="📚")
st.title("📚 DS-408-RAG-Agent 考研智能答疑")

# ==================== 【你要的说明 + 表格 + 简介】 ====================
st.markdown("""
### 程序简要说明
本系统为 **王道408数据结构知识库问答系统**，基于 ReAct Agent 架构，集成检索、推理、对比、总结能力。

### 可用工具
| 工具 | 功能 | 提问示例 |
|------|------|------------|
| 知识检索 ds_knowledge_search | 从PDF知识库查找相关内容 | 1、简述栈的基本定义与特点<br>2、红黑树是什么 |
| 概念对比 ds_concept_compare | 对比两个易混淆概念 | 1、区分顺序表与链表优缺点<br>2、对比深度优先与广度优先遍历 |
| 章节总结 ds_chapter_summary | 输出指定章节核心考点 | 1、总结树结构高频考试知识点<br>2、对比各类排序算法 |

> 🤖 Agent 会自动判断需要调用哪个工具，无需手动指定  
> 📍 回答后会自动展示参考资料的文件及页码定位
""", unsafe_allow_html=True)


# ==================== 初始化 RAG 和 Agent（延迟初始化）====================
@st.cache_resource
def init_services():
    from rag.ds_rag_service import DSRagService
    from react_agent import ReactAgent

    rag = DSRagService(data_path=None)
    agent = ReactAgent()
    return rag, agent


try:
    rag, agent = init_services()
    st.success("✅ 知识库加载成功 | Agent 准备就绪")
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

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_answer
    })