<div align="center">

# HotSearch - 热搜悬浮窗

**一款轻量级桌面热搜聚合工具，三平台实时热点，悬浮置顶，一键直达**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [项目结构](#-项目结构) • [打包部署](#-打包部署)

</div>

---

## ✨ 功能特性

<table>
<tr>
<td width="50%">

### 🔥 三榜聚合
实时抓取 **百度热搜**、**微博热搜**、**IT之家热门资讯**，支持单榜查看或三榜合并展示，每 5 分钟自动刷新。

### 🖥️ 桌面悬浮
无边框置顶窗口，自由拖拽移动，右下角手柄调节大小，透明度 30%~100% 可调。

### 🎨 主题与配色
内置深色 / 浅色两套主题一键切换，也支持通过拾色器自定义标题栏、文字、序号等任意控件颜色。

</td>
<td width="50%">

### 📌 系统托盘
点击 ✕ 最小化到系统托盘，右键菜单支持显示 / 隐藏 / 退出，不占用任务栏。

### 🚀 开机自启
通过 Windows 注册表实现开机自动运行，托盘右键菜单随时开关，无需额外配置。

### 🔗 点击跳转
点击任意热搜标题，自动在浏览器中打开对应详情页或搜索引擎结果页。

</td>
</tr>
</table>

## 🚀 快速开始

### 环境要求

- **Python** 3.12+
- **Edge WebDriver** — [下载地址](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)，将 `msedgedriver.exe` 放到项目根目录

### 安装依赖

```bash
pip install requests lxml parsel selenium pystray Pillow
```

### 运行

```bash
python main.py
```

启动后即可看到桌面悬浮窗，默认加载三榜数据。

## 📁 项目结构

```
hot_all/
├── main.py              # 程序入口，事件绑定与主循环
├── ui.py                # UI 控件创建、数据渲染、颜色刷新
├── config.py            # 常量定义、主题配色、共享配色引用
├── tray.py              # 系统托盘图标与右键菜单 (pystray)
├── auto_start.py        # Windows 注册表开机自启管理
└── spiders/
    ├── __init__.py
    ├── baidu.py         # 百度热搜爬虫 (requests + lxml XPath)
    ├── weibo.py         # 微博热搜爬虫 (Selenium + Edge WebDriver)
    └── ithome.py        # IT之家热门爬虫 (requests + parsel CSS)
```

## 📦 打包部署

使用 PyInstaller 打包为单文件 exe：

```bash
pip install pyinstaller

pyinstaller --onefile --noconsole --icon=app_icon.ico \
    --hidden-import=selenium \
    --hidden-import=lxml \
    --hidden-import=parsel \
    --hidden-import=pystray \
    --hidden-import=PIL \
    --name=HotSearch main.py
```

> **注意：** 打包后将 `msedgedriver.exe` 复制到 `dist/` 目录，与 `HotSearch.exe` 放在同一层级。

## 🛠️ 技术栈

| 模块 | 技术方案 | 说明 |
|:-----|:---------|:-----|
| GUI 框架 | `tkinter` | Python 内置 GUI，轻量无边框窗口 |
| 百度爬虫 | `requests` + `lxml` | HTTP 请求 + XPath 解析 |
| 微博爬虫 | `Selenium` + Edge | 无头浏览器渲染动态页面 |
| IT之家爬虫 | `requests` + `parsel` | HTTP 请求 + CSS 选择器 |
| 系统托盘 | `pystray` + `Pillow` | 跨平台托盘图标 + 图片生成 |
| 开机自启 | `winreg` | Windows 注册表读写 |
| 打包发布 | `PyInstaller` | 单文件 exe 打包 |

## 📜 License

[MIT](LICENSE)
