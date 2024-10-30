import requests
import json
import logging
import time
import os
from config.settings import API_KEY, API_URL, NETWORK
from utils.logger import ColorLogger

# 强制禁用所有代理设置
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""


class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False  # 不使用环境变量中的代理设置
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        }


def optimize_chinese_text(input_text, retries=NETWORK["retries"]):
    """调用 GPT API 优化文本"""
    try:
        ColorLogger.custom("=" * 100, "")  # 加长分隔线
        ColorLogger.custom("📝 原始文本:", "")
        ColorLogger.custom(f"  {input_text}", "")
        ColorLogger.custom("-" * 100, "")  # 加长分隔线

        logging.info(f"正在优化文本: {input_text}")

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一位中文优化专家。你的任务是改进用户输入的中文文本，使其更加清晰、专业、优雅。"
                        "要求：\n"
                        "1. 保持原文的核心意思\n"
                        "2. 使表达更加简洁自然\n"
                        "3. 纠正语法错误\n"
                        "4. 提高表达的专业性\n"
                        "5. 直接返回优化后的文本，不要添加任何解释或说明\n"
                        "6. 如果原文已经很好，可以保持不变"
                    ),
                },
                {"role": "user", "content": input_text},
            ],
            "temperature": 0.7,
            "max_tokens": 1200,
            "presence_penalty": 0.1,
            "frequency_penalty": 0.1,
        }

        client = APIClient()

        for attempt in range(retries):
            try:
                ColorLogger.custom("/* API 请求开始 */", "")  # 添加分隔符
                response = client.session.post(
                    API_URL,
                    headers=client.headers,
                    data=json.dumps(data).encode("utf-8"),
                    proxies=NETWORK["proxy_settings"] if NETWORK["use_proxy"] else None,
                    verify=NETWORK["verify_ssl"],
                    timeout=NETWORK["timeout"],
                )
                ColorLogger.custom("/* API 请求结束 */\n", "")  # 添加分隔符

                response.raise_for_status()

                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and result["choices"]:
                        optimized_text = result["choices"][0]["message"]["content"]
                        ColorLogger.custom("-" * 100, "")  # 加长分隔线
                        ColorLogger.custom("✨ 优化结果:", "")
                        ColorLogger.custom(f"  {optimized_text}", "")
                        ColorLogger.custom("=" * 100 + "\n", "")  # 加长分隔线
                        return optimized_text
                else:
                    ColorLogger.error(
                        f"API 请求失败: {response.status_code} - {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                ColorLogger.error(f"请求异常 (第{attempt + 1}次): {str(e)}")
                if attempt == retries - 1:  # 最后一次重试
                    raise
                time.sleep(1)

    except Exception as e:
        ColorLogger.error(f"优化过程中发生错误: {str(e)}")
        return input_text

    return input_text  # 如果所有重试都失败，返回原文
