# 系统库
import logging
import os
from datetime import datetime
# 本地工具
from utils.path_tool import get_abs_path


#日志保存的根目录
LOG_ROOT = get_abs_path("logs")

#确保日志目录存在
os.makedirs(LOG_ROOT, exist_ok=True)

#日志格式配置
DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

#创建 / 获取日志对象
def get_logger(
        name: str = "agent",                #给日志器起名字，默认叫agent
        console_level: int = logging.INFO,  #控制台输出的日志级别默认只输出 INFO 及以上（INFO/WARNING/ERROR）
        file_level: int = logging.DEBUG,    #日志文件输出的级别，默认记录 DEBUG 及以上所有日志
        log_file = None,                    #指定日志保存到哪个文件，不传就用默认日志文件
) -> logging.Logger:                        #函数最终会返回一个日志对象
    logger = logging.getLogger(name)        #核心，根据以上参数获取 / 创建一个日志器实例
    logger.setLevel(logging.DEBUG)          #给logger对象设置全局日志级别，低于这个级别的日志会被丢弃，不被任何handler处理

    #避免重复添加handler
    if logger.handlers:
        return logger


    #可以配置若干个handler处理器，先配置控制台的handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)         #在上面函数传参中配置了
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)#上面配置过了
    logger.addHandler(console_handler)



    #配置文件handler，调用日志工具后，日志不仅在控制台显示，而且会写入文件
    if not log_file:
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file,encoding="utf-8")
    file_handler.setLevel(file_level)               #在上面函数传参中配置了
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)   #上面配置过了
    logger.addHandler(file_handler)


    return logger

#快捷获取日志器
logger = get_logger()