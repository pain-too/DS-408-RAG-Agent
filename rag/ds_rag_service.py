# 系统模块
import os
import re
from typing import List, Optional
# 第三方库
from langchain_core.documents import Document
# Agent 项目模块
from utils.config_handler import chroma_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger
from model.factory import embedding_model
# RAG 核心模块
from rag.KnowledgeBaseService import KnowledgeBaseService
from rag.vector_store import VectorStoreService


class DSRagService:
    def __init__(self, data_path: Optional[str] = None) -> None:
        logger.info("=" * 60)
        logger.info("开始初始化 DSRagService...")

        # ===================== 配置读取 =====================
        try:
            self.k_default_k:int = chroma_conf.get("k", 3)
            self.k_data_path:str = chroma_conf.get("data_path", "./data")
            logger.info(f"配置读取成功 | k={self.k_default_k}, data_path={self.k_data_path}")

        except Exception as e:
            logger.error(f"读取配置失败：{str(e)}")
            raise RuntimeError("DSRagService 初始化失败：配置加载异常") from e

        # ===================== 初始化kb_service =====================
        try:
            self.kb_service: KnowledgeBaseService = KnowledgeBaseService()
            logger.info("KnowledgeBaseService 初始化成功")

            self.vector_service: VectorStoreService = VectorStoreService(embedding=embedding_model)
            self.vector_service.vector_store = self.kb_service.chroma
            logger.info("VectorStoreService 绑定向量库成功")

        except Exception as e:
            logger.error(f"服务初始化失败：{str(e)}")
            raise RuntimeError("DSRagService 服务初始化异常") from e

        # ===================== 本地版本：自动加载PDF =====================
        # =============== 线上运行：直接使用数据库，不加载文件 ===============
        """
        if data_path is None:
            data_path = get_abs_path(self.k_data_path)

        logger.info(f"自动加载知识库目录：{data_path}")
        self.pdf_upload_folder_with_md5(data_path)

        logger.info("DSRagService 初始化完成 ✅")
        """
        logger.info("✅ 直接使用已上传的向量库，跳过PDF加载")
        logger.info("=" * 60)


    def pdf_upload_folder_with_md5(self, folder_path: str) -> None:
        try:
            abs_folder = get_abs_path(folder_path)
            file_list = os.listdir(abs_folder)
            logger.info(f"扫描目录文件总数：{len(file_list)} 个")

            pdf_count = 0
            for file_name in file_list:
                file_path = os.path.join(abs_folder, file_name)

                if not os.path.isfile(file_path):
                    continue
                if not file_name.lower().endswith(".pdf"):
                    continue

                pdf_count += 1
                logger.info(f"正在处理 PDF：{file_name}")
                result = self.kb_service.upload_entire_pdf(file_path, file_name)
                logger.info(f"处理完成：{file_name} | 结果：{result}")
            logger.info(f"本次共加载 {pdf_count} 个PDF文件")

        except Exception as e:
            logger.error(f"批量加载PDF失败：{str(e)}")


    def format_docs(self, docs: List[Document]) -> str:
        """
        获取带页码、来源的格式化文档，并拼接成最终返回字符串

        KnowledgeBaseService中的定义：
            page.metadata["source"] = file_name
            page.metadata["page_num"] = page_num
        """
        if not docs:
            logger.warning("无文档可格式化")
            return "未找到相关资料"

        formatted_list = []
        idx = 1

        for doc in docs:
            #  先使用当前序号
            source = doc.metadata.get("source", "未知文件")
            page = doc.metadata.get("page_num") or doc.metadata.get("page") or 1
            page = max(int(page), 1)
            content = doc.page_content.strip()
            # 用当前的 idx
            item = f"【参考资料{idx} | {source} 第{page}页】\n{content} "
            formatted_list.append(item)
            # 2. 用完以后序号遍历
            idx += 1
        return "\n\n".join(formatted_list)


    def extract_location_only(self, formatted_text: str) -> str:
        """
        只提取定位，去掉正文内容，仅返回页码。
        正则是为了匹配上方formatted_docs自定义的定位格式
        """
        if not formatted_text:
            return ""
        pattern = r'【参考资料\d+ \| [^】]+?第\d+页】'

        #系统正则模块re.findall返回列表套字符串
        location_lines = re.findall(pattern, formatted_text)
        if location_lines:
            return "\n".join(location_lines)
        else:
            return ""


    def search(self, query: str, k: Optional[int] = None, mode: str = "full") -> str:
        """
            mode是自定义参数，有full和location_only两种模式
        """
        try:
            k = k or self.k_default_k
            retriever = self.vector_service.get_retriever(search_kwargs={"k": k})
            docs = retriever.invoke(query)

            if not docs:
                return "未在王道408数据结构知识库中找到相关内容"
            #调用上方的自定义函数，将检索的文档格式化
            full_formatted = self.format_docs(docs)

            if mode == "location_only":
                return self.extract_location_only(full_formatted)
            return full_formatted

        except Exception as e:
            logger.error(f"检索执行异常：{str(e)}")
            return f"检索服务暂时不可用：{str(e)}"



# ===================== 单例模式 =====================
_rag_service_instance: Optional[DSRagService] = None

def get_rag_service() -> DSRagService:
    """
    获取唯一的DSRagService，避免重复创建
    """
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = DSRagService()
    return _rag_service_instance