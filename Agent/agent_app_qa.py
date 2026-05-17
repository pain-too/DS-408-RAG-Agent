import streamlit as st
from rag.ds_rag_service import DSRagService
from react_agent import ReactAgent

# 页面配置
st.set_page_config(page_title="408答疑助手", page_icon="📚")
st.title("📚 王道408数据结构智能答疑助手")

# -------------------- 程序说明 --------------------
st.markdown("""
### 程序简要说明
本系统为 **王道408数据结构知识库问答系统**，基于 ReAct Agent 架构，集成检索、推理、对比、总结能力。

### 可用工具
| 工具 | 功能 | 使用场景 |
|------|------|----------|
| 🔍 知识检索 | 从PDF知识库查找相关内容 | 问概念、定义、性质 |
| ⚖️ 概念对比 | 对比两个易混淆概念 | 问区别、对比 |
| 📝 章节总结 | 输出指定章节核心考点 | 问总结、归纳 |

### 提问示例
- 二叉树和二叉搜索树的区别是什么
- 请总结图的最短路径算法
- 快速排序和归并排序对比
- 栈和队列的区别
- 红黑树的定义和性质

> 🤖 Agent 会自动判断需要调用哪个工具，无需手动指定
""")

# 初始化会话
if "messages" not in st.session_state:
    st.session_state.messages = []

# 只初始化一次 RAG + Agent
if "rag" not in st.session_state:
    with st.spinner("正在加载知识库..."):
        st.session_state.rag = DSRagService()
if "agent" not in st.session_state:
    st.session_state.agent = ReactAgent()

# 展示历史聊天
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入
prompt = st.chat_input("请输入你的问题...")

if prompt:
    # 显示用户问题
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 回答（Agent 自动决策）
    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent 正在思考..."):
            full_answer = ""
            placeholder = st.empty()

            # Agent 流式执行（自动调用工具）
            for chunk in st.session_state.agent.execute_stream(prompt):
                full_answer += chunk
                placeholder.markdown(full_answer)

    # 保存历史
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_answer
    })