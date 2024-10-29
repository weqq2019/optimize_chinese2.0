import requests
import json
import logging
import pyperclip
import time
from colorama import Fore, Style, init
from config import API_KEY
import threading
from pystray import Icon, MenuItem as item, Menu
from PIL import Image, ImageDraw
import keyboard

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

    # 添加状态检查，防止重复触发
    if not hasattr(on_f9, "is_running"):
        on_f9.is_running = False

    if on_f9.is_running:
        logging.warning("上一次优化任务还在进行中，请稍后再试...")
        return

    on_f9.is_running = True

    try:
        # 确保图标存在且可用
        if icon and icon.visible:
            icon.icon = create_image("red")  # 设置为红色，表示任务进行中
    except Exception as e:
        logging.error(f"更新图标状态失败: {str(e)}")

    def optimize_task():
        global successful_optimizations
        try:
            original_clipboard = pyperclip.paste()
            # 增加剪贴板操作的重试机制
            max_retries = 3
            for _ in range(max_retries):
                try:
                    keyboard.press_and_release("ctrl+c")
                    time.sleep(0.3)  # 增加等待时间
                    input_text = pyperclip.paste()
                    if input_text and input_text.strip():
                        break
                except Exception as e:
                    logging.warning(f"剪贴板操作失败，正在重试: {str(e)}")
                    time.sleep(0.2)
            else:
                print(f"{Fore.YELLOW}无法获取选中的文本，请重试。{Style.RESET_ALL}")
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
            try:
                if icon and icon.visible:
                    icon.icon = create_image("green")  # 恢复为绿色
            except Exception as e:
                logging.error(f"恢复图标状态失败: {str(e)}")
            on_f9.is_running = False

    # 启动优化任务线程
    threading.Thread(target=optimize_task, name="OptimizeTask").start()


def quit_action(icon, item):
    """退出程序"""
    icon.visible = False
    icon.stop()
    print(f"\n{Fore.MAGENTA}程序已退出{Style.RESET_ALL}")


def setup_tray():
    """设置托盘图标和菜单"""
    global icon
    try:
        menu = Menu(
            item("状态: 运行中", lambda: None, enabled=False), item("退出", quit_action)
        )
        icon = Icon("GPT Optimizer", create_image("green"), menu=menu)
        icon.run()  # 这会阻塞当前线程
    except Exception as e:
        logging.error(f"设置托盘图标失败: {str(e)}")
        raise  # 重新抛出异常，确保主程序知道托盘初始化失败


def main():
    """程序入口"""
    print(f"{Fore.MAGENTA}程序启动中...{Style.RESET_ALL}")

    # 启动托盘线程，但不设为daemon线程
    tray_thread = threading.Thread(target=setup_tray, name="TrayThread")
    tray_thread.start()

    # 等待托盘图标初始化完成
    time.sleep(1)

    print(f"{Fore.MAGENTA}程序已启动{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}选中文本并按下 F9 来优化...{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}右键托盘图标可退出程序{Style.RESET_ALL}")

    keyboard.add_hotkey("f9", on_f9, suppress=True)
    logging.info("程序已启动，等待用户操作...")

    try:
        # 保持主线程运行，直到托盘线程结束
        tray_thread.join()
    except KeyboardInterrupt:
        if icon:
            icon.stop()
        print(f"\n{Fore.MAGENTA}程序被用户中断{Style.RESET_ALL}")
    finally:
        logging.info("程序结束")


if __name__ == "__main__":
    main()
