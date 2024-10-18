import requests
import json
import keyboard
import logging
import pyperclip
import time
from colorama import Fore, Style, init
from config import API_KEY
import threading
from pystray import Icon, MenuItem as item, Menu
from PIL import Image, ImageDraw

# 初始化 colorama
init(autoreset=True)

# 设置日志
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# API 设置
API_URL = "https://api.openai-hk.com/v1/chat/completions"
optimized_texts = []  # 累计优化文本的列表
successful_optimizations = 0  # 成功优化次数计数器

# 初始化托盘图标
icon = None  # 全局托盘图标变量


def create_image(color):
    """创建指定颜色的图标"""
    image = Image.new("RGB", (64, 64), color)
    draw = ImageDraw.Draw(image)
    draw.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
    return image


def optimize_chinese_text(input_text, retries=3):
    """调用 GPT API 优化文本"""
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
                    "content": (
                        "你是一位语言优化助手，帮助用户改进中文表达，使其更加简洁、自然、流畅、优雅，并确保逻辑连贯和表达精准。"
                        "请直接返回优化后的文本，不要添加任何额外的解释。"
                    ),
                },
                {"role": "user", "content": input_text},
            ],
        }

        json_data = json.dumps(data, ensure_ascii=False).encode("utf-8")

        for attempt in range(retries):
            response = requests.post(
                API_URL,
                headers=headers,
                data=json_data,
                proxies={"http": None, "https": None},
            )
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    optimized_text = result["choices"][0]["message"]["content"]
                    logging.info(f"优化完成: {optimized_text}")
                    return optimized_text
                else:
                    logging.error(f"API 响应中没有找到优化后的文本: {result}")
                    return input_text
            elif response.status_code == 428:
                logging.warning("请求条件未满足，正在重试...")
                time.sleep(1)
            else:
                response.raise_for_status()
    except Exception as e:
        logging.error(f"优化过程中发生错误: {str(e)}")
        return input_text


def on_f9():
    """按下 F9 触发优化，并切换托盘图标状态"""
    global successful_optimizations, icon

    icon.icon = create_image("red")  # 设置为红色，表示任务进行中

    def optimize_task():
        global successful_optimizations
        try:
            original_clipboard = pyperclip.paste()
            keyboard.press_and_release("ctrl+c")
            time.sleep(0.2)
            input_text = pyperclip.paste()

            if not input_text.strip():
                print(
                    f"{Fore.YELLOW}未选中文本，请选中文本后再按 F9。{Style.RESET_ALL}"
                )
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

        except Exception as e:
            logging.error(f"处理 F9 热键时发生错误: {str(e)}")
            print(f"{Fore.RED}处理 F9 热键时发生错误: {str(e)}{Style.RESET_ALL}")

        finally:
            icon.icon = create_image("green")  # 恢复为绿色

    # 启动优化任务线程
    threading.Thread(target=optimize_task).start()


def quit_action(icon, item):
    """退出程序"""
    icon.stop()
    print(f"\n{Fore.MAGENTA}程序已退出{Style.RESET_ALL}")


def setup_tray():
    """设置托盘图标和菜单"""
    global icon
    icon = Icon(
        "GPT Optimizer",
        create_image("green"),
        menu=Menu(item("Quit", quit_action)),
    )
    icon.run()


def main():
    """程序入口"""
    # 启动托盘线程
    tray_thread = threading.Thread(target=setup_tray)
    tray_thread.daemon = True
    tray_thread.start()

    print(f"{Fore.MAGENTA}程序已启动{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}选中文本并按下 F9 来优化...{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}按 Ctrl+C 来退出程序{Style.RESET_ALL}")

    keyboard.add_hotkey("f9", on_f9, suppress=True)
    logging.info("程序已启动，等待用户操作...")

    try:
        while True:
            time.sleep(0.1)  # 主线程保持运行
    except KeyboardInterrupt:
        print(f"\n{Fore.MAGENTA}程序被用户中断{Style.RESET_ALL}")
    finally:
        logging.info("程序结束")


if __name__ == "__main__":
    main()
