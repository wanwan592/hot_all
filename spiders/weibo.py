# spiders/weibo.py
import os
import sys
import traceback
# 显式导入 Edge 子模块（Selenium 4 用 __getattr__ 懒加载，PyInstaller 检测不到）
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


def _log(msg):
    """写日志到文件（打包后 print 无效，用文件记录）"""
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass


def get_weibo_hot():
    """使用 Edge WebDriver 获取微博热搜（无需 Cookie）"""
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

        # 优先使用 Selenium Manager 自动管理驱动（Selenium 4.6+）
        # 如果失败，回退到手动指定的 msedgedriver.exe
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

        driver.get('https://s.weibo.com/top/summary?cate=realtimehot')
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_top_realtimehot tbody tr')))
        rows = driver.find_elements(By.CSS_SELECTOR, '#pl_top_realtimehot tbody tr')
        result = []
        for idx, tr in enumerate(rows, 1):
            try:
                title_elem = tr.find_element(By.CSS_SELECTOR, '.td-02 a')
                title = title_elem.text.strip()
                if not title:
                    continue
                hot_elem = tr.find_element(By.CSS_SELECTOR, '.td-02 span')
                hot = hot_elem.text.strip() if hot_elem else '无热度'
                result.append({'排名': idx, '标题': title, '热度': hot})
            except Exception:
                continue
        _log(f"成功获取 {len(result)} 条微博热搜")
        return result
    except Exception as e:
        _log(f"微博爬取错误：{e}")
        _log(traceback.format_exc())
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
