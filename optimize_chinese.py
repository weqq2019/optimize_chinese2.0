import requests
import json
import keyboard
import logging
import pyperclip
import time
from colorama import Fore, Style, init
from config import API_KEY

# 初始化 colorama
init(autoreset=True)

# 设置日志
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# API 设置
API_URL = "https://api.openai-hk.com/v1/chat/completions"

# 用于累计优化文本的列表
optimized_texts = []

# 初始化成功优化次数
successful_optimizations = 0


def optimize_chinese_text(input_text):
    try:
        logging.info(f"正在优化文本: {input_text}")

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {API_KEY}",
        }

        data = {
            "max_tokens": 1200,
            "model": "gpt-3.5-turbo",
            "temperature": 0.8,
            "top_p": 1,
            "presence_penalty": 1,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位语言优化助手，帮助用户改进中文表达，使其更通顺。请直接返回优化后的文本，不要添加任何额外的解释。",
                },
                {"role": "user", "content": input_text},
            ],
        }

        json_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        response = requests.post(API_URL, headers=headers, data=json_data)
        response.raise_for_status()  # 如果请求失败，这将引发一个异常
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            optimized_text = result["choices"][0]["message"]["content"]
            logging.info(f"优化完成: {optimized_text}")
            return optimized_text
        else:
            logging.error(f"API 响应中没有找到优化后的文本: {result}")
            return input_text
    except requests.exceptions.RequestException as e:
        logging.error(f"API 请求错误: {str(e)}")
        return input_text
    except json.JSONDecodeError as e:
        logging.error(f"JSON 解码错误: {str(e)}")
        return input_text
    except Exception as e:
        logging.error(f"优化过程中发生错误: {str(e)}")
        return input_text


def on_f9():
    global successful_optimizations
    try:
        original_clipboard = pyperclip.paste()
        keyboard.press_and_release("ctrl+c")
        time.sleep(0.2)
        input_text = pyperclip.paste()

        if not input_text.strip():
            print(f"{Fore.YELLOW}未选中文本，请选中文本后再按 F9。{Style.RESET_ALL}")
            return

        logging.info(f"用户选中的文本: {input_text}")

        optimized_text = optimize_chinese_text(input_text)
        optimized_texts.append((input_text, optimized_text))

        if input_text != optimized_text:
            successful_optimizations += 1

        pyperclip.copy(optimized_text)
        time.sleep(0.2)

        keyboard.press_and_release("ctrl+v")

        time.sleep(0.2)
        pyperclip.copy(original_clipboard)

        print(f"\n{Fore.GREEN}原文: {Fore.YELLOW}{input_text}")
        print(f"{Fore.GREEN}优化后: {Fore.CYAN}{optimized_text}{Style.RESET_ALL}")
        print(
            f"{Fore.MAGENTA}成功优化次数: {Fore.WHITE}{successful_optimizations}{Style.RESET_ALL}"
        )

        logging.info("文本已被优化并替换")
    except Exception as e:
        logging.error(f"处理 F9 热键时发生错误: {str(e)}")


# def on_f10():
#     print(f"\n{Fore.MAGENTA}所有优化的文本：{Style.RESET_ALL}")
#     for i, (original, optimized) in enumerate(optimized_texts, 1):
#         print(f"\n{Fore.BLUE}优化 #{i}:")
#         print(f"{Fore.GREEN}原文: {Fore.YELLOW}{original}")
#         print(f"{Fore.GREEN}优化后: {Fore.CYAN}{optimized}{Style.RESET_ALL}")
#     print(
#         f"\n{Fore.MAGENTA}总共成功优化次数: {Fore.WHITE}{successful_optimizations}{Style.RESET_ALL}"
#     )


def main():
    global successful_optimizations
    try:
        print(f"{Fore.MAGENTA}程序已启动{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}选中文本并按下 F9 来优化...{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}按 Ctrl+C 来退出程序{Style.RESET_ALL}")

        keyboard.add_hotkey("f9", on_f9)

        logging.info("程序已启动，等待用户操作...")

        # 无限循环，直到用户手动中断程序!!!
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print(f"\n{Fore.MAGENTA}程序被用户中断{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"主程序中发生错误: {str(e)}")
    finally:
        print(
            f"\n{Fore.MAGENTA}程序结束，总共成功优化次数: {Fore.WHITE}{successful_optimizations}{Style.RESET_ALL}"
        )
        logging.info("程序结束")


if __name__ == "__main__":
    main()
