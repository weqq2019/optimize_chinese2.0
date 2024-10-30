import os

# API 设置
API_KEY = os.getenv(
    "OPENAI_API_KEY", "hk-r1oy9u10000441583dfa911d5fd8600a2ee0c6a78749f5c6"
)
API_URL = "https://api.openai-hk.com/v1/chat/completions"

# 日志设置
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = "DEBUG"

# 热键设置
HOTKEYS = ["f9", "ctrl+alt+space"]

# 托盘图标设置
TRAY_TITLE = "GPT 优化助手"
ICON_SIZE = (64, 64)
ICON_COLORS = {"active": "green", "processing": "red"}

# 网络设置
NETWORK = {
    "use_proxy": False,  # 是否使用代理
    "proxy_settings": {
        "http": None,  # HTTP 代理，例如 "http://127.0.0.1:7890"
        "https": None,  # HTTPS 代理
        "no_proxy": "*",  # 不使用代理的域名
    },
    "timeout": 10,  # 请求超时时间（秒）
    "retries": 3,  # 请求重试次数
    "verify_ssl": True,  # 是否验证 SSL 证书
}
