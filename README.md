# hot_all - 热搜悬浮窗

一个轻量级桌面悬浮窗应用，实时聚合百度、微博、IT之家三平台热搜数据，支持置顶显示、透明度调节、主题切换，可最小化到系统托盘并开机自启。

![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 功能特性

- **三榜聚合** — 百度热搜、微博热搜、IT之家热门资讯，一键切换或合并展示
- **桌面悬浮** — 无边框置顶窗口，支持拖拽移动和右下角缩放手柄
- **主题切换** — 内置深色/浅色两套主题，也支持自定义任意控件颜色
- **系统托盘** — 点击关闭按钮最小化到托盘，右键菜单可恢复/隐藏/退出
- **开机自启** — 通过 Windows 注册表实现开机自动运行，托盘菜单可随时开关
- **点击跳转** — 点击热搜标题直接在浏览器中打开对应详情页
- **自动刷新** — 每 5 分钟自动抓取最新数据

## 项目结构

```
hot_all/
├── main.py              # 程序入口，事件绑定与主循环
├── ui.py                # UI 创建、渲染、颜色刷新
├── config.py            # 常量、主题配色、共享配色引用
├── tray.py              # 系统托盘图标与右键菜单
├── auto_start.py        # Windows 注册表开机自启管理
└── spiders/
    ├── __init__.py
    ├── baidu.py         # 百度热搜爬虫 (requests + lxml)
    ├── weibo.py         # 微博热搜爬虫 (selenium + Edge)
    └── ithome.py        # IT之家热门爬虫 (requests + parsel)
```

## 环境依赖

```bash
pip install requests lxml parsel selenium pystray Pillow
```

微博热搜模块需要 [Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)，将 `msedgedriver.exe` 放在项目根目录。

## 运行

```bash
python main.py
```

## 打包为 exe

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=app_icon.ico \
    --hidden-import=selenium --hidden-import=lxml --hidden-import=parsel \
    --hidden-import=pystray --hidden-import=PIL \
    --name=HotSearch main.py
```

打包后将 `msedgedriver.exe` 复制到 `dist/` 目录与 `HotSearch.exe` 同目录即可运行。

## 技术栈

| 模块 | 技术 |
|------|------|
| GUI | tkinter |
| 百度爬虫 | requests + lxml (XPath) |
| 微博爬虫 | Selenium + Edge WebDriver |
| IT之家爬虫 | requests + parsel (CSS 选择器) |
| 系统托盘 | pystray + Pillow |
| 开机自启 | winreg (Windows 注册表) |
| 打包 | PyInstaller |
