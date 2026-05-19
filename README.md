# 📚 DS-408-RAG-Agent

> 基于 RAG + ReAct Agent 的王道408考研智能答疑系统 | [在线Demo](https://ds-408-rag-agent.streamlit.app)

## ✨ 核心亮点

- **📍 页码溯源**：检索结果精确到【文件名 第X页】，全链路保留 `source` 和 `page_num` 元数据，回答可验证
- **🔧 ReAct Agent**：自动选择检索/对比/总结工具，实现“思考-调用-回答”闭环
- **🧹 入库清洗**：自动去除水印、页码、PPT噪声词，提升检索质量
- **⚙️ 配置解耦**：YAML 集中管理 + 独立 Prompt 模板，换模型/改参数无需改代码
- **💾 MD5去重**：已入库 PDF 自动跳过，避免重复处理

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python |
| 大模型 | 通义千问 (DashScope) |
| 向量库 | ChromaDB |
| 框架 | LangChain + ReAct Agent |
| 配置管理 | YAML |
| 前端 | Streamlit |
| 部署 | Streamlit Cloud |

## 📂 项目结构

```text
DS-408-RAG-Agent/
├── requirements.txt
├── .gitignore
│
├── ingest.py                     # 文档入库入口：PDF批量向量化
├── react_agent.py                # **ReAct 智能推理循环**（核心功能）
├── agent_app_qa.py               # 智能问答主入口
│
├── rag/                          # RAG 检索增强模块
│   ├── ds_rag_service.py            # RAG 核心业务逻辑
│   ├── KnowledgeBaseService.py      # （特色功能）**PDF水印自动去除 + 结构化知识点解析**
│   ├── vector_store.py              # 向量库存储与相似度检索
│   └── file_history_store.py        # （特色功能）**长对话记忆 / 历史上下文持久化**
│
├── model/                        # 模型工厂
│   └── factory.py                   # 大模型 & 嵌入模型统一管理
│
├── config/                       # 配置中心（YAML 工程化）
│   ├── agent.yml                    # Agent 工具与参数配置
│   ├── rag.yml                      # 分块、检索策略配置
│   ├── chroma.yml                   # 向量库持久化配置
│   └── prompts.yml                  # 提示词模板配置
│
├── prompts/                      # 提示词模块
│   └── main_prompt.txt              # 408考研专属系统提示词
│
├── tools/                        # 工具模块
│   └── agent_tools.py               # 多工具调用支持
│
├── utils/                        # 通用工具
│   ├── config_handler.py            # 配置加载
│   ├── file_handler.py              # 文件处理工具
│   ├── logger_handler.py            # 日志系统
│   ├── path_tool.py                 # 路径管理
│   └── prompt_loader.py             # 提示词加载
│
└── data/                         # 408考研教材PDF存放目录

```