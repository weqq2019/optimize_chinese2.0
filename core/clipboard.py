import win32clipboard
import win32con
import logging
from threading import Lock
import time


class ClipboardManager:
    def __init__(self):
        self.clipboard_lock = Lock()

    def get_text(self):
        """获取剪贴板文本"""
        with self.clipboard_lock:
            for attempt in range(3):
                try:
                    win32clipboard.OpenClipboard(0)
                    try:
                        if win32clipboard.IsClipboardFormatAvailable(
                            win32con.CF_UNICODETEXT
                        ):
                            data = win32clipboard.GetClipboardData(
                                win32con.CF_UNICODETEXT
                            )
                            return str(data) if data else ""
                    finally:
                        win32clipboard.CloseClipboard()
                except Exception as e:
                    logging.warning(f"获取剪贴板文本失败 (第{attempt + 1}次): {str(e)}")
                    time.sleep(0.2)
            return ""

    def set_text(self, text):
        """设置剪贴板文本"""
        if not isinstance(text, str):
            text = str(text)

        with self.clipboard_lock:
            for attempt in range(3):
                try:
                    win32clipboard.OpenClipboard(0)
                    try:
                        win32clipboard.EmptyClipboard()
                        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
                        return True
                    finally:
                        win32clipboard.CloseClipboard()
                except Exception as e:
                    logging.warning(f"设置剪贴板文本失败 (第{attempt + 1}次): {str(e)}")
                    if "invalid character" in str(e):
                        logging.debug(f"问题文本: {repr(text)}")
                    time.sleep(0.2)
            return False

    def clear(self):
        """清空剪贴板"""
        with self.clipboard_lock:
            try:
                win32clipboard.OpenClipboard(0)
                try:
                    win32clipboard.EmptyClipboard()
                    return True
                finally:
                    win32clipboard.CloseClipboard()
            except Exception as e:
                logging.error(f"清空剪贴板失败: {str(e)}")
                return False
