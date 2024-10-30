import threading
import time
from colorama import Fore, Style
from utils.logger import ColorLogger
from core.clipboard import ClipboardManager
from core.optimizer import optimize_chinese_text
import keyboard


class TextProcessor:
    def __init__(self, tray_manager):
        self.tray_manager = tray_manager
        self.clipboard_manager = ClipboardManager()
        self.successful_optimizations = 0

    def process_text(self):
        """处理文本优化任务"""
        ColorLogger.processing("开始处理...")
        self.tray_manager.set_processing(True)

        try:
            # 保存原始剪贴板内容
            original_clipboard = self.clipboard_manager.get_text()

            # 获取选中文本
            input_text = self._get_selected_text()
            if not input_text:
                return

            # 优化文本
            ColorLogger.info("正在优化文本...")
            optimized_text = optimize_chinese_text(input_text)

            # 更新文本
            if self._update_text(optimized_text):
                if input_text != optimized_text:
                    self.successful_optimizations += 1
                    self._show_result(input_text, optimized_text)

            # 恢复原始剪贴板
            self.clipboard_manager.set_text(original_clipboard)

        except Exception as e:
            ColorLogger.error(f"处理失败: {str(e)}")
        finally:
            self.tray_manager.set_processing(False)

    def _get_selected_text(self):
        """获取选中的文本"""
        for retry in range(3):
            try:
                time.sleep(0.1)
                keyboard.press_and_release("ctrl+c")
                time.sleep(0.3)

                text = self.clipboard_manager.get_text()
                if text and text.strip():
                    return text

                ColorLogger.warning(f"尝试获取文本中 (第{retry + 1}次)...")
                time.sleep(0.2)
            except Exception as e:
                ColorLogger.warning(f"剪贴板操作失败，正在重试 (第{retry + 1}次)...")
                time.sleep(0.3)

        ColorLogger.error("无法获取选中的文本，请确保已选中文本后重试。")
        return None

    def _update_text(self, text):
        """更新文本"""
        ColorLogger.info("正在更新剪贴板...")
        for retry in range(3):
            if self.clipboard_manager.set_text(text):
                time.sleep(0.2)
                keyboard.press_and_release("ctrl+v")
                time.sleep(0.2)
                return True
            ColorLogger.warning(f"更新剪贴板重试中 (第{retry + 1}次)...")
            time.sleep(0.3)
        return False

    def _show_result(self, input_text, optimized_text):
        """显示优化结果"""
        ColorLogger.success(f"优化成功！成功优化次数: {self.successful_optimizations}")
