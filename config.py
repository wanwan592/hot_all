# config.py - 常量与主题配色

# 零宽隐藏字符，用于区分平台
MARK_BAIDU = "\u200B"
MARK_WEIBO = "\u200C"
MARK_ITHOME = "\u200D"

# 两套主题配色
theme_dark = {
    "root_bg": "#1f2937",
    "title_bg": "#374151",
    "text_bg": "#1f2937",
    "text_normal": "#f3f4f6",
    "text_gray": "#9ca3af",
    "index_color": "#60a5fa",
    "grip_color": "#6b7280"
}

theme_light = {
    "root_bg": "#f3f4f6",
    "title_bg": "#e5e7eb",
    "text_bg": "#f3f4f6",
    "text_normal": "#111827",
    "text_gray": "#6b7280",
    "index_color": "#2563eb",
    "grip_color": "#9ca3af"
}

# 窗口尺寸限制
MIN_WIDTH = 620
MIN_HEIGHT = 400
BASE_WIDTH = 640
MIN_FONT_SIZE = 8
MAX_FONT_SIZE = 14

# 当前激活的配色（可变共享引用，main/ui 均通过 in-place 修改此对象）
current_color = theme_dark.copy()
