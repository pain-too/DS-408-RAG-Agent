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
| 工具 | 功能  | 提问示例 |
|------|------|------------|
| 知识检索ds_knowledge_search | 从PDF知识库查找相关内容 | 1、简述栈的基本定义与特点  <br> 2、红黑树是什么 |
| 概念对比ds_concept_compare | 对比两个易混淆概念 | 1、区分顺序表与链表优缺点  <br> 2、对比深度优先与广度优先遍历 |
| 章节总结ds_chapter_summary | 输出指定章节核心考点 | 1、总结树结构高频考试知识点  <br> 2、对比各类排序算法 |

> 🤖 Agent 会自动判断需要调用哪个工具，无需手动指定  
> 📍 回答后会自动展示参考资料的文件及页码定位
""", unsafe_allow_html = True)

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
        # 展示历史消息的资料定位（如果有）
        if msg.get("location"):
            with st.expander("📍 参考资料定位", expanded=False):
                st.markdown(f"```\n{msg['location']}\n```")

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
                placeholder.markdown(full_answer, unsafe_allow_html=True)  # 兼容Agent返回的换行

            # ========== 核心补充：调用资料定位功能 ==========
            with st.spinner("📍 正在检索参考资料定位..."):
                # 调用 RAG 的 location_only 模式获取资料定位
                location_info = st.session_state.rag.search(
                    query=prompt,
                    mode="location_only"  # 核心：仅返回定位信息
                )

            # 展示资料定位（折叠面板，不干扰主回答）
            if location_info and location_info != "未在王道408数据结构知识库中找到相关内容":
                with st.expander("📍 参考资料定位", expanded=True):
                    st.markdown(f"```\n{location_info}\n```")
            else:
                st.caption("📍 未检索到相关参考资料定位")

    # 保存历史（包含定位信息）
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_answer,
        "location": location_info  # 存储定位信息，用于历史展示
    })