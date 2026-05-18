# 系统库
import os
import hashlib
# 第三方库
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
# 本地工具
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


# 获取文件的md5十六进制指纹
# 成功返回字符串md5，失败返回None
def get_file_md5_hex(file_path: str) -> str | None:
    # 统一转绝对路径
    file_path = get_abs_path(file_path)

    if not os.path.exists(file_path):
        logger.error(f"[md5计算]文件{file_path}不存在")
        return None
    if not os.path.isfile(file_path):
        logger.error(f"[md5计算]文件{file_path}不是文件")
        return None

    md5_obj = hashlib.md5()
    chunk_size = 4096  # 4KB分片，避免文件过大
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)

        hex_md5 = md5_obj.hexdigest()
        return hex_md5
    except Exception as e:
        logger.error(f"计算文件 {file_path} 的md5失败,{str(e)}")
        return None


# 返回文件夹内的文件列表
def listdir_with_allowed_type(path: str, allowed_type: tuple[str]) -> list[str]:
    files = []
    # 统一转绝对路径
    path = get_abs_path(path)

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]{path}不是文件夹")
        return files

    for f in os.listdir(path):
        # 拼接完整路径
        full_path = get_abs_path(os.path.join(path, f))

        # 规避非文件的情况
        if os.path.isfile(full_path) and f.endswith(allowed_type):
            files.append(full_path)

    return files


# 加载PDF
def pdf_loader(file_path: str, password: str = "") -> list[Document]:
    # 统一转绝对路径
    file_path = get_abs_path(file_path)

    try:
        return PyPDFLoader(file_path, password).load()
    except Exception as e:
        logger.error(f"加载PDF失败 {file_path}: {str(e)}")
        return []