# tray.py — 系统托盘图标、右键菜单
import threading
from PIL import Image, ImageDraw
import pystray

from auto_start import is_auto_start_enabled, toggle_auto_start


def _create_icon_image():
    """用 Pillow 生成一个简单的托盘图标（橙色火焰）"""
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # 外圈橙色圆
    draw.ellipse([4, 4, 60, 60], fill=(251, 146, 60))
    # 内圈深橙色圆
    draw.ellipse([16, 16, 48, 48], fill=(234, 88, 12))
    # 中心白点
    draw.ellipse([26, 26, 38, 38], fill=(255, 255, 255))
    return img


def setup_tray(root, on_exit):
    """
    创建并启动系统托盘图标（后台守护线程）。

    参数:
        root     — tkinter 的 Tk 实例
        on_exit  — 真正退出程序时的回调（用于清理资源）
    """

    def _show_window(icon=None, item=None):
        root.after(0, root.deiconify)

    def _hide_window(icon=None, item=None):
        root.after(0, root.withdraw)

    def _exit_app(icon=None, item=None):
        icon.stop()
        on_exit()

    def _on_toggle_auto_start(icon=None, item=None):
        toggle_auto_start()

    # 构建右键菜单
    menu = pystray.Menu(
        pystray.MenuItem("显示窗口", _show_window, default=True),
        pystray.MenuItem("隐藏窗口", _hide_window),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            "开机自启",
            _on_toggle_auto_start,
            checked=lambda item: is_auto_start_enabled()
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("退出", _exit_app),
    )

    icon = pystray.Icon(
        name="hot_all",
        icon=_create_icon_image(),
        title="热搜悬浮窗",
        menu=menu,
    )

    # 在守护线程中运行，不阻塞 tkinter 主循环
    t = threading.Thread(target=icon.run, daemon=True)
    t.start()
    return icon
