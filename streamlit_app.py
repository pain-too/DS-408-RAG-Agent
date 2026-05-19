import streamlit as st
import os
from model.factory import ChatModelFactory
from rag.ds_rag_service import get_rag_service

# 从 Streamlit secrets 读取 key
os.environ["DASHSCOPE_API_KEY"] = st.secrets["DASHSCOPE_API_KEY"]

st.title("📚 DS-408-RAG-Agent 考研智能答疑")

# 初始化 RAG
rag = get_rag_service()

# 对话历史
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入
prompt = st.chat_input("请输入你的问题...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = rag.qa_chain(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})