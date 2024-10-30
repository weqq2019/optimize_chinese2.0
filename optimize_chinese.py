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
import psutil
import win32clipboard
import win32con
from threading import Lock

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
                    return optimized_text
                else:
                    logging.error(f"API 响应中没有找到优化后的文本: {result}")
                    return input_text
            elif response.status_code == 428:
                logging.warning("求条件未满足，正在重试...")
                time.sleep(1)
            else:
                response.raise_for_status()
    except Exception as e:
        logging.error(f"优化过程中发生错误: {str(e)}")
        return input_text


class ClipboardManager:
    """更可靠的剪贴板管理"""

    def __init__(self):
        self.clipboard_lock = Lock()

    def get_text(self):
        """获取剪贴板文本，带重试机制"""
        with self.clipboard_lock:
            for attempt in range(3):  # 最多重试3次
                try:
                    win32clipboard.OpenClipboard()
                    try:
                        if win32clipboard.IsClipboardFormatAvailable(
                            win32con.CF_UNICODETEXT
                        ):
                            text = win32clipboard.GetClipboardData(
                                win32con.CF_UNICODETEXT
                            )
                            return text
                    finally:
                        win32clipboard.CloseClipboard()
                except Exception as e:
                    logging.warning(f"获取剪贴板文本失败 (第{attempt + 1}次): {str(e)}")
                    time.sleep(0.2)  # 短暂等待后重试
            return ""

    def set_text(self, text):
        """设置剪贴板文本，带重试机制"""
        with self.clipboard_lock:
            for attempt in range(3):  # 最多重试3次
                try:
                    win32clipboard.OpenClipboard()
                    try:
                        win32clipboard.EmptyClipboard()
                        win32clipboard.SetClipboardText(text)
                        return True
                    finally:
                        win32clipboard.CloseClipboard()
                except Exception as e:
                    logging.warning(f"设置剪贴板文本失败 (第{attempt + 1}次): {str(e)}")
                    time.sleep(0.2)  # 短暂等待后重试
            return False


def on_f9():
    """按下 F9 触发优化，并切换托盘图标状态"""
    global successful_optimizations, icon

    if not hasattr(on_f9, "is_running"):
        on_f9.is_running = False

    if on_f9.is_running:
        print(
            f"{Fore.YELLOW}⚠️ 上一次优化任务还在进行中，请稍后再试...{Style.RESET_ALL}"
        )
        return

    on_f9.is_running = True
    print(f"{Fore.CYAN}🔄 开始处理...{Style.RESET_ALL}")

    # 立即更新托盘图标为红色（处理中）
    try:
        if icon and icon.visible:
            icon.update_menu()  # 确保菜单更新
            icon.icon = create_image("red")
            print(f"{Fore.CYAN}🔄 托盘图标已切换为处理中状态{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"更新托盘图标状态失败: {str(e)}")

    def optimize_task():
        global successful_optimizations
        clipboard_manager = ClipboardManager()

        try:
            # 保存原始剪贴板内容
            original_clipboard = clipboard_manager.get_text()

            # 获取选中文本
            input_text = ""
            for retry in range(3):
                try:
                    # 先等待一下确保选中状态稳定
                    time.sleep(0.1)
                    keyboard.press_and_release("ctrl+c")
                    time.sleep(0.3)  # 等待复制完成

                    input_text = clipboard_manager.get_text()
                    if input_text and input_text.strip():
                        break

                    print(
                        f"{Fore.YELLOW}⚠️ 尝试获取文本中 (第{retry + 1}次)...{Style.RESET_ALL}"
                    )
                    time.sleep(0.2)
                except Exception as e:
                    print(
                        f"{Fore.YELLOW}⚠️ 剪贴板操作失败，正在重试 (第{retry + 1}次)...{Style.RESET_ALL}"
                    )
                    time.sleep(0.3)

            if not input_text.strip():
                print(
                    f"{Fore.RED}❌ 无法获取选中的文本，请确保已选中文本后重试。{Style.RESET_ALL}"
                )
                return

            print(f"{Fore.CYAN}✨ 正在优化文本...{Style.RESET_ALL}")
            optimized_text = optimize_chinese_text(input_text)

            # 更新剪贴板并粘贴
            print(f"{Fore.CYAN}📋 正在更新剪贴板...{Style.RESET_ALL}")
            success = False
            for retry in range(3):
                if clipboard_manager.set_text(optimized_text):
                    time.sleep(0.2)
                    keyboard.press_and_release("ctrl+v")
                    time.sleep(0.2)
                    success = True
                    break
                print(
                    f"{Fore.YELLOW}⚠️ 更新剪贴板重试中 (第{retry + 1}次)...{Style.RESET_ALL}"
                )
                time.sleep(0.3)

            # 恢复原始剪贴板
            clipboard_manager.set_text(original_clipboard)

            if success:
                if input_text != optimized_text:
                    successful_optimizations += 1
                print(f"\n{Fore.GREEN}✅ 优化成功！{Style.RESET_ALL}")
                print(f"{Fore.GREEN}原文: {Fore.YELLOW}{input_text}")
                print(
                    f"{Fore.GREEN}优化后: {Fore.CYAN}{optimized_text}{Style.RESET_ALL}"
                )
                print(
                    f"{Fore.MAGENTA}成功优化次数: {Fore.WHITE}{successful_optimizations}{Style.RESET_ALL}"
                )
            else:
                print(f"{Fore.RED}❌ 剪贴板操作失败，请重试{Style.RESET_ALL}")

        except Exception as e:
            logging.error(f"处理失败: {str(e)}")
            print(f"{Fore.RED}❌ 发生错误: {str(e)}{Style.RESET_ALL}")

        finally:
            # 恢复托盘图标为绿色（空闲状态）
            try:
                if icon and icon.visible:
                    icon.update_menu()  # 确保菜单更新
                    icon.icon = create_image("green")
                    print(f"{Fore.GREEN}✅ 托盘图标已恢复为空闲状态{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"恢复托盘图标状态失败: {str(e)}")

            on_f9.is_running = False
            print(f"{Fore.CYAN}✨ 处理完成，可以继续使用热键{Style.RESET_ALL}")

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
        icon = Icon(
            "GPT Optimizer",
            create_image("green"),
            menu=menu,
            title="GPT 优化助手",  # 添加悬停提示
        )
        icon.run()
    except Exception as e:
        logging.error(f"设置托盘图标失败: {str(e)}")
        raise


def main():
    """程序入口"""
    print(f"{Fore.MAGENTA}程序启动中...{Style.RESET_ALL}")

    # 启动托盘线程
    tray_thread = threading.Thread(target=setup_tray, name="TrayThread", daemon=True)
    tray_thread.start()

    time.sleep(1)

    print(f"{Fore.MAGENTA}程序已启动{Style.RESET_ALL}")

    # 设置热键，同时支持 F9 和 Ctrl+Alt+Space
    try:
        keyboard.add_hotkey("f9", on_f9, suppress=True)
        keyboard.add_hotkey("ctrl+alt+space", on_f9, suppress=True)
        print(f"{Fore.GREEN}✅ 热键已设置: F9 或 Ctrl+Alt+Space{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ 热键注册失败: {str(e)}{Style.RESET_ALL}")
        return

    print(f"{Fore.MAGENTA}选中文本后按 F9 或 Ctrl+Alt+Space 来优化...{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}按 Ctrl+C 来退出程序{Style.RESET_ALL}")

    logging.info("程序已启动，等待用户操作...")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        if icon:
            icon.visible = False
            icon.stop()
        print(f"\n{Fore.MAGENTA}程序被用户中断{Style.RESET_ALL}")
    finally:
        logging.info("程序结束")


if __name__ == "__main__":
    main()
