# spiders/weibo.py
import os
import sys
import time
import traceback
import requests

# Selenium 相关作为兜底方案延迟导入，避免 API 可用时仍强依赖 Edge 驱动
from selenium.webdriver.edge.webdriver import WebDriver as EdgeWebDriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 定位 msedgedriver.exe：
# - 打包后：sys.executable 指向 HotSearch.exe，驱动在同目录
# - 开发环境：驱动在项目根目录（spiders/ 的上一级）
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVER_PATH = os.path.join(BASE_DIR, 'msedgedriver.exe')
LOG_PATH = os.path.join(BASE_DIR, 'weibo_error.log')
MAX_LOG_BYTES = 512 * 1024  # 日志超过 512KB 自动截断，防止无限增长

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")


def _rotate_log_if_needed():
    """日志超过阈值时保留尾部内容，避免无限增长"""
    try:
        if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > MAX_LOG_BYTES:
            with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            with open(LOG_PATH, 'w', encoding='utf-8') as f:
                f.writelines(lines[-200:])  # 保留最近 200 行
    except Exception:
        pass


def _log(msg):
    """写日志到文件（打包后 print 无效，用文件记录）"""
    try:
        _rotate_log_if_needed()
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass


def _fetch_via_api():
    """方案一：轻量 JSON API，无需浏览器，速度快、稳定性高"""
    url = 'https://weibo.com/ajax/side/hotSearch'
    headers = {
        'User-Agent': UA,
        'Referer': 'https://weibo.com/',
        'Accept': 'application/json, text/plain, */*',
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.encoding = 'utf-8'
            data = resp.json()
            realtime = data.get('data', {}).get('realtime', [])
            result = []
            for item in realtime:
                title = (item.get('word') or '').strip()
                if not title:
                    continue
                num = item.get('num') or 0
                hot = f"{num:,}" if isinstance(num, int) else str(num)
                result.append({'排名': len(result) + 1, '标题': title, '热度': hot})
            if result:
                _log(f"API 成功获取 {len(result)} 条微博热搜")
                return result
            _log("API 返回空列表")
            return None
        except Exception as e:
            _log(f"微博 API 失败 (第 {attempt + 1}/{max_retries} 次): {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1.5 * (attempt + 1))  # 递增退避 1.5s / 3s
    return None


def _fetch_via_selenium():
    """方案二（兜底）：Selenium 无头 Edge 渲染动态页面"""
    driver = None
    try:
        options = EdgeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1280,800')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # 优先使用 Selenium Manager 自动管理驱动，失败回退手动指定
        try:
            driver = EdgeWebDriver(options=options)
        except Exception as e1:
            _log(f"Selenium Manager 启动失败: {e1}，尝试手动指定驱动")
            if os.path.exists(DRIVER_PATH):
                service = EdgeService(DRIVER_PATH)
                driver = EdgeWebDriver(service=service, options=options)
            else:
                _log(f"手动驱动也不存在: {DRIVER_PATH}")
                return None

        driver.set_page_load_timeout(30)
        driver.get('https://s.weibo.com/top/summary?cate=realtimehot')
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_top_realtimehot tbody tr')))
        rows = driver.find_elements(By.CSS_SELECTOR, '#pl_top_realtimehot tbody tr')
        result = []
        for idx, tr in enumerate(rows, 1):
            try:
                title_elem = tr.find_element(By.CSS_SELECTOR, '.td-02 a')
                title = title_elem.text.strip()
                if not title:
                    continue
                try:
                    hot = tr.find_element(By.CSS_SELECTOR, '.td-02 span').text.strip() or '无热度'
                except Exception:
                    hot = '无热度'
                result.append({'排名': len(result) + 1, '标题': title, '热度': hot})
            except Exception:
                continue
        _log(f"Selenium 成功获取 {len(result)} 条微博热搜")
        return result or None
    except Exception as e:
        _log(f"Selenium 爬取错误：{type(e).__name__}: {e}")
        _log(traceback.format_exc())
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def get_weibo_hot():
    """获取微博热搜：优先 JSON API，失败回退 Selenium，返回列表或 None"""
    _log("=== 开始获取微博热搜 ===")
    result = _fetch_via_api()
    if result:
        return result
    _log("API 不可用，回退 Selenium 方案")
    return _fetch_via_selenium()
