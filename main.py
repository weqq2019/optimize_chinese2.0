import threading
import time
from utils.logger import setup_logger, ColorLogger
from core.tray import TrayManager
from core.hotkey import HotkeyManager
from core.processor import TextProcessor


def main():
    """主程序入口"""
    # 设置日志
    setup_logger()
    ColorLogger.info("程序启动中...")

    try:
        # 初始化托盘管理器
        tray_manager = TrayManager()

        # 初始化文本处理器
        processor = TextProcessor(tray_manager)

        # 初始化热键管理器
        hotkey_manager = HotkeyManager()

        # 启动托盘
        def quit_action(icon, item):
            icon.visible = False
            icon.stop()
            ColorLogger.info("程序已退出")

        icon = tray_manager.setup(quit_action)
        tray_thread = threading.Thread(target=icon.run, daemon=True)
        tray_thread.start()

        time.sleep(1)  # 等待托盘初始化

        # 注册热键
        if not hotkey_manager.register_hotkeys(processor.process_text):
            ColorLogger.error("热键注册失败，程序退出")
            return

        ColorLogger.success("程序已启动")
        ColorLogger.info("选中文本后按热键来优化...")
        ColorLogger.info("按 Ctrl+C 来退出程序")

        # 主循环
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        if tray_manager.icon:
            tray_manager.icon.visible = False
            tray_manager.icon.stop()
        ColorLogger.info("程序被用户中断")
    except Exception as e:
        ColorLogger.error(f"程序发生错误: {str(e)}")
    finally:
        ColorLogger.info("程序已退出")


if __name__ == "__main__":
    main()
