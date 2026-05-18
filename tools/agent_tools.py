from langchain_core.tools import tool
from rag.ds_rag_service import get_rag_service

rag_service = get_rag_service()

@tool
def ds_knowledge_search(query: str) -> str:
    """
    王道408数据结构 —— 知识点检索工具
    """
    result = rag_service.search(query, mode="location_only") # 👈 修复
    if not result:
        return "未在王道408数据结构资料库检索到相关内容，请换一种提问方式。"
    return result

@tool
def ds_concept_compare(query: str) -> str:
    """
    王道408数据结构 —— 易混概念对比辨析工具
    """
    context = rag_service.search(query, mode="location_only") # 👈 修复

    ans = f"""
# 408数据结构易混概念对比分析
## 对比对象：{query}

## 对比维度（考研标准）
1. 定义与结构特点
2. 时间/空间复杂度
3. 适用场景
4. 优点与缺点
5. 408 高频考点

## 王道教材原文参考
{context}
"""
    return ans

@tool
def ds_chapter_summary(chapter_name: str) -> str:
    """
    王道408数据结构 —— 章节知识点归纳工具
    """
    context = rag_service.search(chapter_name, mode="location_only") # 👈 修复

    ans = f"""
# 408数据结构「{chapter_name}」章节归纳
## 归纳维度（适配考研）
1. 核心概念
2. 必考算法
3. 时间/空间复杂度
4. 易错点 & 常考题型
5. 真题关联考点

## 王道教材原文参考
{context}
"""
    return ans