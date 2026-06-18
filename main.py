# main.py - 程序入口
import tkinter as tk
from tkinter import colorchooser
import threading
import time
import webbrowser
from config import *
from spiders import get_baidu_hot, get_weibo_hot, get_ithome_hot
from ui import create_ui, render_hot_data, update_font_size, refresh_all_colors
from tray import setup_tray

# 全局状态
show_mode = 0
cache_baidu = None
cache_weibo = None
cache_ithome = None
win_lock = False
current_font_size = 10
text_box = None
root = None
tray_icon = None

def main():
    global root, text_box, tray_icon

    root = tk.Tk()
    root.title("热搜悬浮窗")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.92)
    root.geometry("640x720+100+100")
    root.minsize(MIN_WIDTH, MIN_HEIGHT)
    root.configure(bg=current_color["root_bg"])

    # 创建UI，获取控件引用
    text_box, buttons, drag_widgets, grip, grip_canvas = create_ui(root)

    # 绑定事件
    # 锁定
    def toggle_lock():
        global win_lock
        win_lock = not win_lock
        buttons['lock'].config(text="🔒" if win_lock else "🔓")
    buttons['lock'].config(command=toggle_lock)

    # 置顶切换
    def toggle_topmost():
        is_top = root.attributes("-topmost")
        root.attributes("-topmost", not is_top)
        buttons['pin'].config(text="📌" if not is_top else "📍")
    buttons['pin'].config(command=toggle_topmost)

    # 主题切换
    def switch_theme():
        if current_color["root_bg"] == theme_dark["root_bg"]:
            current_color.clear()
            current_color.update(theme_light)
            buttons['theme'].config(text="🌙")
        else:
            current_color.clear()
            current_color.update(theme_dark)
            buttons['theme'].config(text="☀️")
        refresh_all_colors(current_color)
    buttons['theme'].config(command=switch_theme)

    # 模式切换
    def switch_show_mode():
        global show_mode
        show_mode = (show_mode + 1) % 4
        txt = ["三榜", "百度", "微博", "IT"][show_mode]
        buttons['mode'].config(text=txt)
        render_hot_data(cache_baidu, cache_weibo, cache_ithome, show_mode)
    buttons['mode'].config(command=switch_show_mode)

    # 字体调节
    def change_font(delta):
        global current_font_size
        new_size = max(MIN_FONT_SIZE, min(24, current_font_size + delta))
        if new_size != current_font_size:
            current_font_size = new_size
            update_font_size(current_font_size)
            root._manual_font_set = True
            root.after(2000, lambda: setattr(root, '_manual_font_set', False))
    buttons['font_minus'].config(command=lambda: change_font(-1))
    buttons['font_plus'].config(command=lambda: change_font(1))

    # 透明度
    def change_alpha(val):
        root.attributes("-alpha", float(val) / 100)
    buttons['alpha_scale'].config(command=change_alpha)

    # 窗口背景色
    def set_whole_window_color():
        c = colorchooser.askcolor(title="选择整个窗体背景色")[1]
        if c:
            current_color["root_bg"] = c
            current_color["text_bg"] = c
            refresh_all_colors(current_color)
    buttons['window_color'].config(command=set_whole_window_color)

    # 自定义配色
    def open_custom_color_panel():
        win = tk.Toplevel(root)
        win.title("高级自定义配色")
        win.geometry("320x280")
        win.configure(bg=current_color["root_bg"])
        def pick_title():
            c = colorchooser.askcolor()[1]
            if c: current_color["title_bg"] = c; refresh_all_colors(current_color)
        def pick_text():
            c = colorchooser.askcolor()[1]
            if c: current_color["text_normal"] = c; refresh_all_colors(current_color)
        def pick_index():
            c = colorchooser.askcolor()[1]
            if c: current_color["index_color"] = c; refresh_all_colors(current_color)
        tk.Button(win, text="1. 修改顶部标题栏", command=pick_title, width=25).pack(pady=4)
        tk.Button(win, text="2. 修改热搜文字颜色", command=pick_text, width=25).pack(pady=4)
        tk.Button(win, text="3. 修改序号高亮颜色", command=pick_index, width=25).pack(pady=4)
        tk.Button(win, text="关闭", command=win.destroy, bg="#ef4444", fg="white").pack(pady=8)
    buttons['custom_color'].config(command=open_custom_color_panel)

    # 关闭 → 最小化到托盘
    def close_win():
        root.withdraw()
    buttons['close'].config(command=close_win)

    # 真正退出（从托盘菜单调用）
    def real_exit():
        if tray_icon:
            try:
                tray_icon.stop()
            except Exception:
                pass
        root.destroy()

    # 系统托盘
    tray_icon = setup_tray(root, on_exit=real_exit)

    # 窗口管理器关闭事件（overrideredirect 模式下某些系统仍会触发）
    root.protocol("WM_DELETE_WINDOW", close_win)

    # 窗口拖动
    drag_win_x = 0
    drag_win_y = 0
    def drag_start(event):
        nonlocal drag_win_x, drag_win_y
        drag_win_x, drag_win_y = event.x, event.y
    def drag_move(event):
        nonlocal drag_win_x, drag_win_y
        if win_lock: return
        new_x = root.winfo_x() + event.x - drag_win_x
        new_y = root.winfo_y() + event.y - drag_win_y
        root.geometry(f"+{new_x}+{new_y}")
    for w in drag_widgets:
        w.bind("<Button-1>", drag_start)
        w.bind("<B1-Motion>", drag_move)

    # 缩放手柄
    resize_active = False
    resize_start_x = resize_start_y = resize_start_w = resize_start_h = 0
    def grip_resize_start(event):
        nonlocal resize_active, resize_start_x, resize_start_y, resize_start_w, resize_start_h
        resize_active = True
        resize_start_x = event.x_root
        resize_start_y = event.y_root
        resize_start_w = root.winfo_width()
        resize_start_h = root.winfo_height()
    def grip_resize_drag(event):
        nonlocal resize_active
        if not resize_active: return
        dw = event.x_root - resize_start_x
        dh = event.y_root - resize_start_y
        new_w = max(MIN_WIDTH, resize_start_w + dw)
        new_h = max(MIN_HEIGHT, resize_start_h + dh)
        root.geometry(f"{new_w}x{new_h}")
    def grip_resize_end(event):
        nonlocal resize_active
        resize_active = False
    for w in [grip, grip_canvas]:
        w.bind("<ButtonPress-1>", grip_resize_start)
        w.bind("<B1-Motion>", grip_resize_drag)
        w.bind("<ButtonRelease-1>", grip_resize_end)

    # 点击跳转
    def jump_search(event):
        pos = text_box.index(f"@{event.x},{event.y} linestart")
        line_full = text_box.get(pos, f"{pos} lineend").strip()
        if not line_full: return
        try:
            if line_full.startswith(MARK_BAIDU):
                title = line_full.replace(MARK_BAIDU, "").split(". ", 1)[1]
                webbrowser.open(f"https://www.baidu.com/s?wd={title}")
            elif line_full.startswith(MARK_WEIBO):
                title = line_full.replace(MARK_WEIBO, "").split(". ", 1)[1]
                webbrowser.open(f"https://s.weibo.com/weibo?q={title}")
            elif line_full.startswith(MARK_ITHOME):
                title = line_full.replace(MARK_ITHOME, "").split(". ", 1)[1]
                # 需要获取ithome链接，此处使用cache_ithome
                for t, link in (cache_ithome or []):
                    if t == title:
                        webbrowser.open(link)
                        break
        except IndexError:
            pass
    text_box.bind("<Button-1>", jump_search)

    # 初始提示
    text_box.insert(tk.END, "⏳ 正在加载数据，请稍候...\n", "loading")
    text_box.insert(tk.END, "💡 点击新闻标题可跳转详情\n", "loading")
    text_box.insert(tk.END, "💡 顶部【三榜/百度/微博/IT】切换源\n", "loading")
    text_box.insert(tk.END, "💡 拖拽右下角调整窗口大小 | A±调节字号", "loading")

    # 启动刷新线程（三个爬虫并行执行，哪个先完成就先显示哪个）
    _cache_lock = threading.Lock()

    def _fetch_and_update(name, fetcher):
        """在独立线程中执行爬虫，完成后调度到主线程更新 UI"""
        global cache_baidu, cache_weibo, cache_ithome
        try:
            result = fetcher()
        except Exception as e:
            print(f"{name}爬取异常：{e}")
            result = None
        # None → 爬虫失败，用 False 标记（None 保留给"尚未加载"状态）
        if result is None:
            result = False
        with _cache_lock:
            if name == "baidu":
                cache_baidu = result
            elif name == "weibo":
                cache_weibo = result
            elif name == "ithome":
                cache_ithome = result
            b, w, i = cache_baidu, cache_weibo, cache_ithome
        root.after(0, render_hot_data, b, w, i, show_mode)

    def refresh_loop():
        while True:
            threads = [
                threading.Thread(target=_fetch_and_update, args=("baidu", get_baidu_hot)),
                threading.Thread(target=_fetch_and_update, args=("weibo", get_weibo_hot)),
                threading.Thread(target=_fetch_and_update, args=("ithome", get_ithome_hot)),
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=60)  # 单个爬虫最多等 60 秒
            time.sleep(300)

    threading.Thread(target=refresh_loop, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()
