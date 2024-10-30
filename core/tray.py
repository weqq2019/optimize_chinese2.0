from pystray import Icon, MenuItem as item, Menu
from PIL import Image, ImageDraw
from config.settings import ICON_SIZE, ICON_COLORS, TRAY_TITLE


class TrayManager:
    def __init__(self):
        self.icon = None

    def create_image(self, color):
        """创建指定颜色的圆形图标"""
        # 创建透明背景的图片
        image = Image.new("RGBA", ICON_SIZE, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 计算圆形的边界
        padding = 4
        left = padding
        top = padding
        right = ICON_SIZE[0] - padding
        bottom = ICON_SIZE[1] - padding

        # 绘制外圆
        draw.ellipse([left, top, right, bottom], fill=color)

        # 绘制内圆（白色）
        inner_padding = 12
        draw.ellipse(
            [
                left + inner_padding,
                top + inner_padding,
                right - inner_padding,
                bottom - inner_padding,
            ],
            fill=(255, 255, 255),
        )

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
