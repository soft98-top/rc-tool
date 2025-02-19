import logging  
import sys  
from logging.handlers import RotatingFileHandler  

def setup_logger(name: str = 'http_request_tool',  
                 log_file: str = 'http_requests.log',  
                 level: int = logging.INFO) -> logging.Logger:  
    """配置日志记录器"""  
    logger = logging.getLogger(name)  
    logger.setLevel(level)  

    logger.handlers.clear()  

    console_handler = logging.StreamHandler(sys.stdout)  
    console_handler.setLevel(level)  

    file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)  
    file_handler.setLevel(level)  

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',  
                                  datefmt='%Y-%m-%d %H:%M:%S')  

    console_handler.setFormatter(formatter)  
    file_handler.setFormatter(formatter)  

    logger.addHandler(console_handler)  
    logger.addHandler(file_handler)  

    return logger