import logging
import os
from datetime import datetime
from colorama import init, Fore, Style
from config.settings import LOG_FORMAT, LOG_LEVEL


def setup_logger():
    """设置日志"""
    init(autoreset=True)  # 初始化 colorama

    # 创建logs目录
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # 设置日志文件名（按日期）
    log_filename = os.path.join(
        log_dir, f"optimize_{datetime.now().strftime('%Y%m%d')}.log"
    )

    # 配置日志
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),  # 文件处理器
            logging.StreamHandler(),  # 控制台处理器
        ],
    )


class ColorLogger:
    """彩色日志输出"""

    logger = logging.getLogger(__name__)

    @staticmethod
    def success(msg):
        logging.info(f"{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")

    @staticmethod
    def info(msg):
        logging.info(f"{Fore.CYAN}ℹ️ {msg}{Style.RESET_ALL}")

    @staticmethod
    def warning(msg):
        logging.warning(f"{Fore.YELLOW}⚠️ {msg}{Style.RESET_ALL}")

    @staticmethod
    def error(msg):
        logging.error(f"{Fore.RED}❌ {msg}{Style.RESET_ALL}")

    @staticmethod
    def processing(msg):
        logging.info(f"{Fore.CYAN}🔄 {msg}{Style.RESET_ALL}")

    @staticmethod
    def custom(msg, color_style):
        """使用自定义颜色输出"""
        logging.info(f"{color_style}{msg}{Style.RESET_ALL}")
