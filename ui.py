# ui.py - 创建界面与渲染
import tkinter as tk
from tkinter import colorchooser
import webbrowser
from config import *

# 全局引用（由 main 设置）
text_box = None
root = None

# ---------- 控件注册表，用于 refresh_all_colors ----------
# 按角色分组存储，方便按 key 批量更新 bg / fg
_widgets = {
    "title_bg_bg": [],       # bg = title_bg
    "title_bg_fg": [],       # fg = text_normal, bg = title_bg
    "text_bg_bg": [],        # bg = text_bg
    "root_bg_bg": [],        # bg = root_bg
    "alpha_scale": None,     # Scale 单独处理
    "close_btn": None,       # 关闭按钮颜色固定，不参与主题
    "grip_canvas": None,     # Canvas 需要重绘线条
    "text_box": None,        # Text 控件
}


def _register(widget, group):
    """把控件注册到对应分组"""
    _widgets[group].append(widget)


def create_ui(master):
    """创建所有 UI 控件，返回文本框对象及各种回调设置"""
    global root, text_box
    root = master

    # 清空注册表（防止重复调用 create_ui）
    for key in _widgets:
        if isinstance(_widgets[key], list):
            _widgets[key].clear()
        else:
            _widgets[key] = None

    # ---- 顶部导航栏 ----
    top_nav = tk.Frame(master, bg=current_color["title_bg"])
    top_nav.pack(fill="x")
    top_nav.config(height=55)
    top_nav.pack_propagate(False)
    _register(top_nav, "title_bg_bg")

    # 左侧组
    left_group = tk.Frame(top_nav, bg=current_color["title_bg"])
    left_group.pack(side="left", padx=(12, 8), pady=4)
    _register(left_group, "title_bg_bg")

    title_label = tk.Label(
        left_group,
        text="热搜榜",
        font=("微软雅黑", 11, "bold"),
        bg=current_color["title_bg"],
        fg=current_color["text_normal"],
        wraplength=100
    )
    title_label.pack(side="left", padx=(0, 6))
    _register(title_label, "title_bg_fg")

    # 锁定按钮
    lock_btn = tk.Button(left_group, text="🔓", bd=0, bg=current_color["title_bg"],
                         fg=current_color["text_normal"], width=2)
    lock_btn.pack(side="left", padx=4)
    _register(lock_btn, "title_bg_fg")

    # 主题切换
    theme_btn = tk.Button(left_group, text="☀️", bd=0, bg=current_color["title_bg"],
                          fg=current_color["text_normal"], width=3)
    theme_btn.pack(side="left", padx=4)
    _register(theme_btn, "title_bg_fg")

    # 模式切换
    mode_btn = tk.Button(left_group, text="三榜", bd=0, bg=current_color["title_bg"],
                         fg=current_color["text_normal"], width=5)
    mode_btn.pack(side="left", padx=4)
    _register(mode_btn, "title_bg_fg")

    # 中间组
    center_group = tk.Frame(top_nav, bg=current_color["title_bg"])
    center_group.pack(side="left", padx=10, pady=4, expand=True, fill="x")
    _register(center_group, "title_bg_bg")

    font_minus_btn = tk.Button(center_group, text="A−", bd=0, bg=current_color["title_bg"],
                               fg=current_color["text_normal"], width=2)
    font_minus_btn.pack(side="left", padx=6)
    _register(font_minus_btn, "title_bg_fg")

    font_plus_btn = tk.Button(center_group, text="A+", bd=0, bg=current_color["title_bg"],
                              fg=current_color["text_normal"], width=2)
    font_plus_btn.pack(side="left", padx=6)
    _register(font_plus_btn, "title_bg_fg")

    alpha_label = tk.Label(center_group, text="透明", bg=current_color["title_bg"],
                           fg=current_color["text_normal"], font=("微软雅黑", 9))
    alpha_label.pack(side="left", padx=(12, 4))
    _register(alpha_label, "title_bg_fg")

    alpha_scale = tk.Scale(center_group, from_=30, to=100, orient="horizontal",
                           length=70, showvalue=0,
                           bg=current_color["title_bg"], fg=current_color["text_normal"],
                           highlightthickness=0)
    alpha_scale.set(92)
    alpha_scale.pack(side="left", padx=4)
    _widgets["alpha_scale"] = alpha_scale

    # 右侧组
    right_group = tk.Frame(top_nav, bg=current_color["title_bg"])
    right_group.pack(side="right", padx=(0, 12), pady=4)
    _register(right_group, "title_bg_bg")

    window_color_btn = tk.Button(right_group, text="🖌️", bd=0, bg=current_color["title_bg"],
                                 fg=current_color["text_normal"], width=2)
    window_color_btn.pack(side="left", padx=4)
    _register(window_color_btn, "title_bg_fg")

    custom_color_btn = tk.Button(right_group, text="🎨", bd=0, bg=current_color["title_bg"],
                                 fg=current_color["text_normal"], width=2)
    custom_color_btn.pack(side="left", padx=4)
    _register(custom_color_btn, "title_bg_fg")

    close_btn = tk.Button(right_group, text="✕", bd=0, bg="#ef4444", fg="white", width=2)
    close_btn.pack(side="left", padx=(8, 0))
    _widgets["close_btn"] = close_btn

    # ---- 底部文本框 ----
    text_frame = tk.Frame(master, bg=current_color["text_bg"])
    text_frame.pack(fill="both", expand=True)
    _register(text_frame, "text_bg_bg")

    text_box = tk.Text(
        text_frame, font=("微软雅黑", 10),
        bg=current_color["text_bg"], fg=current_color["text_normal"],
        bd=0, padx=8, pady=8, cursor="hand2"
    )
    text_box.pack(fill="both", expand=True)
    text_box.tag_config("index", foreground=current_color["index_color"], font=("微软雅黑", 10, "bold"))
    text_box.tag_config("content", foreground=current_color["text_normal"])
    text_box.tag_config("loading", foreground=current_color["text_gray"])
    text_box.tag_config("title_split", foreground="#fb923c", font=("微软雅黑", 11, "bold"))
    _widgets["text_box"] = text_box

    # ---- 缩放手柄 ----
    grip_size = 16
    grip = tk.Frame(master, bg=current_color["root_bg"], width=grip_size, height=grip_size,
                    cursor="bottom_right_corner")
    grip.place(relx=1.0, rely=1.0, anchor="se")
    _register(grip, "root_bg_bg")

    grip_canvas = tk.Canvas(grip, width=grip_size, height=grip_size,
                            bg=current_color["root_bg"], highlightthickness=0)
    grip_canvas.pack(fill="both", expand=True)
    _register(grip_canvas, "root_bg_bg")
    _widgets["grip_canvas"] = grip_canvas
    draw_grip_lines(grip_canvas)

    # 返回需要外部绑定的控件和回调函数接口
    buttons = {
        'lock': lock_btn,
        'theme': theme_btn,
        'mode': mode_btn,
        'font_minus': font_minus_btn,
        'font_plus': font_plus_btn,
        'window_color': window_color_btn,
        'custom_color': custom_color_btn,
        'close': close_btn,
        'alpha_scale': alpha_scale,
    }
    drag_widgets = [top_nav, left_group, center_group, right_group, title_label]

    return text_box, buttons, drag_widgets, grip, grip_canvas


def draw_grip_lines(canvas):
    canvas.delete("all")
    c = current_color.get("grip_color", "#6b7280")
    size = 16
    for i in range(3):
        offset = 4 + i * 4
        canvas.create_line(size - offset, size - 2, size - 2, size - offset, fill=c, width=1)


def render_hot_data(baidu_data, weibo_data, ithome_data, show_mode):
    """渲染数据到文本框"""
    global text_box
    text_box.delete(1.0, tk.END)

    if show_mode == 0:  # 三榜
        # 百度
        text_box.insert(tk.END, "===== 百度实时热搜 =====\n\n", "title_split")
        if baidu_data:
            for idx, title in enumerate(baidu_data[:15], 1):
                text_box.insert(tk.END, MARK_BAIDU, "content")
                text_box.insert(tk.END, f"{idx}. ", "index")
                text_box.insert(tk.END, f"{title}\n", "content")
        elif baidu_data is None:
            text_box.insert(tk.END, "⏳ 正在爬取百度热搜...\n", "loading")
        else:
            text_box.insert(tk.END, "❌ 百度热搜获取失败\n", "loading")
        text_box.insert(tk.END, "\n", "content")

        # 微博
        text_box.insert(tk.END, "===== 微博实时热搜 =====\n\n", "title_split")
        if weibo_data:
            for item in weibo_data[:15]:
                text_box.insert(tk.END, MARK_WEIBO, "content")
                text_box.insert(tk.END, f"{item['排名']}. ", "index")
                text_box.insert(tk.END, f"{item['标题']}\n", "content")
        elif weibo_data is None:
            text_box.insert(tk.END, "⏳ 正在爬取微博热搜...\n", "loading")
        else:
            text_box.insert(tk.END, "❌ 微博热搜获取失败\n", "loading")
        text_box.insert(tk.END, "\n", "content")

        # IT之家
        text_box.insert(tk.END, "===== IT之家 热门资讯 =====\n\n", "title_split")
        if ithome_data:
            for idx, (title, link) in enumerate(ithome_data[:15], 1):
                text_box.insert(tk.END, MARK_ITHOME, "content")
                text_box.insert(tk.END, f"{idx}. ", "index")
                text_box.insert(tk.END, f"{title}\n", "content")
        elif ithome_data is None:
            text_box.insert(tk.END, "⏳ 正在爬取IT之家资讯...\n", "loading")
        else:
            text_box.insert(tk.END, "❌ IT之家资讯获取失败\n", "loading")

    elif show_mode == 1:  # 仅百度
        text_box.insert(tk.END, "===== 百度实时热搜 =====\n\n", "title_split")
        if baidu_data:
            for idx, title in enumerate(baidu_data[:15], 1):
                text_box.insert(tk.END, MARK_BAIDU, "content")
                text_box.insert(tk.END, f"{idx}. ", "index")
                text_box.insert(tk.END, f"{title}\n", "content")
        elif baidu_data is None:
            text_box.insert(tk.END, "⏳ 正在爬取百度热搜...\n", "loading")
        else:
            text_box.insert(tk.END, "❌ 百度热搜获取失败\n", "loading")

    elif show_mode == 2:  # 仅微博
        text_box.insert(tk.END, "===== 微博实时热搜 =====\n\n", "title_split")
        if weibo_data:
            for item in weibo_data[:15]:
                text_box.insert(tk.END, MARK_WEIBO, "content")
                text_box.insert(tk.END, f"{item['排名']}. ", "index")
                text_box.insert(tk.END, f"{item['标题']}\n", "content")
        elif weibo_data is None:
            text_box.insert(tk.END, "⏳ 正在爬取微博热搜...\n", "loading")
        else:
            text_box.insert(tk.END, "❌ 微博热搜获取失败\n", "loading")

    elif show_mode == 3:  # 仅IT之家
        text_box.insert(tk.END, "===== IT之家 热门资讯 =====\n\n", "title_split")
        if ithome_data:
            for idx, (title, link) in enumerate(ithome_data[:15], 1):
                text_box.insert(tk.END, MARK_ITHOME, "content")
                text_box.insert(tk.END, f"{idx}. ", "index")
                text_box.insert(tk.END, f"{title}\n", "content")
        elif ithome_data is None:
            text_box.insert(tk.END, "⏳ 正在爬取IT之家资讯...\n", "loading")
        else:
            text_box.insert(tk.END, "❌ IT之家资讯获取失败\n", "loading")

    text_box.insert(tk.END, "\n🔄 5分钟后自动刷新", "loading")


def update_font_size(size):
    """更新文本框字体大小"""
    global text_box
    text_box.configure(font=("微软雅黑", size))
    text_box.tag_config("index", font=("微软雅黑", size, "bold"))
    text_box.tag_config("title_split", font=("微软雅黑", size + 1, "bold"))


def refresh_all_colors(color_dict):
    """遍历注册表，刷新所有 UI 控件颜色"""
    global root, text_box

    title_bg = color_dict["title_bg"]
    text_normal = color_dict["text_normal"]
    text_bg = color_dict["text_bg"]
    root_bg = color_dict["root_bg"]
    index_color = color_dict["index_color"]
    text_gray = color_dict["text_gray"]

    # 窗口根背景
    root.configure(bg=root_bg)

    # bg = title_bg 的 Frame / Canvas
    for w in _widgets["title_bg_bg"]:
        w.configure(bg=title_bg)

    # bg = title_bg, fg = text_normal 的 Button / Label
    for w in _widgets["title_bg_fg"]:
        w.configure(bg=title_bg, fg=text_normal)

    # bg = text_bg 的 Frame
    for w in _widgets["text_bg_bg"]:
        w.configure(bg=text_bg)

    # bg = root_bg 的 Frame / Canvas
    for w in _widgets["root_bg_bg"]:
        w.configure(bg=root_bg)

    # Scale 控件
    if _widgets["alpha_scale"]:
        _widgets["alpha_scale"].configure(bg=title_bg, fg=text_normal)

    # Text 控件 + tag 颜色
    tb = _widgets["text_box"]
    if tb:
        tb.configure(bg=text_bg, fg=text_normal)
        tb.tag_config("index", foreground=index_color)
        tb.tag_config("content", foreground=text_normal)
        tb.tag_config("loading", foreground=text_gray)

    # 缩放手柄重绘线条
    gc = _widgets["grip_canvas"]
    if gc:
        draw_grip_lines(gc)
