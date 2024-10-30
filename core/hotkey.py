import keyboard
import logging
from config.settings import HOTKEYS


class HotkeyManager:
    def __init__(self):
        self.is_running = False
        self.callback = None

    def register_hotkeys(self, callback):
        """注册热键"""
        self.callback = callback
        try:
            for hotkey in HOTKEYS:
                keyboard.add_hotkey(hotkey, self._handle_hotkey, suppress=True)
            logging.info(f"热键已设置: {' 或 '.join(HOTKEYS)}")
            return True
        except Exception as e:
            logging.error(f"热键注册失败: {str(e)}")
            return False

    def _handle_hotkey(self):
        """热键处理函数"""
        if not self.is_running and self.callback:
            self.is_running = True
            try:
                self.callback()
            finally:
                self.is_running = False
