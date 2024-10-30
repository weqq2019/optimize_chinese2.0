from pystray import Icon, MenuItem as item, Menu
from PIL import Image, ImageDraw
from config.settings import ICON_SIZE, ICON_COLORS, TRAY_TITLE


class TrayManager:
    def __init__(self):
        self.icon = None

    def create_image(self, color):
        """创建指定颜色的图标"""
        image = Image.new("RGB", ICON_SIZE, color)
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
        return image

    def setup(self, quit_callback):
        """设置托盘图标"""
        menu = Menu(
            item("状态: 运行中", lambda: None, enabled=False),
            item("退出", quit_callback),
        )
        self.icon = Icon(
            TRAY_TITLE,
            self.create_image(ICON_COLORS["active"]),
            menu=menu,
            title=TRAY_TITLE,
        )
        return self.icon

    def set_processing(self, is_processing):
        """设置处理状态"""
        if self.icon and self.icon.visible:
            color = (
                ICON_COLORS["processing"] if is_processing else ICON_COLORS["active"]
            )
            self.icon.icon = self.create_image(color)
            self.icon.update_menu()
