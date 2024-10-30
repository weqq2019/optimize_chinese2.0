import requests
import json
import os

# 强制禁用所有代理设置
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""

url = "https://api.openai-hk.com/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer hk-r1oy9u10000441583dfa911d5fd8600a2ee0c6a78749f5c6",
}

data = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "你好，这是一个测试消息"}],
    "temperature": 0.8,
    "max_tokens": 1200,
}

try:
    print("正在发送请求...")

    # 创建会话并禁用代理
    session = requests.Session()
    session.trust_env = False  # 不使用环境变量中的代理设置

    response = session.post(
        url,
        headers=headers,
        data=json.dumps(data).encode("utf-8"),
        proxies={"http": None, "https": None, "no_proxy": "*"},
        verify=True,  # 启用 SSL 验证
    )

    print(f"\n状态码: {response.status_code}")
    print(f"响应内容: {response.text}")

except Exception as e:
    print(f"发生错误: {str(e)}")
