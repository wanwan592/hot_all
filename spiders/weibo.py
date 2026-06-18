# spiders/weibo.py
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 获取当前文件所在目录，用于定位驱动（假设驱动放在项目根目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVER_PATH = os.path.join(BASE_DIR, 'msedgedriver.exe')

def get_weibo_hot():
    """使用 Edge WebDriver 获取微博热搜（无需 Cookie）"""
    if not os.path.exists(DRIVER_PATH):
        print(f"Edge WebDriver 未找到: {DRIVER_PATH}")
        return None

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1280,800')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=options)
    try:
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
        return result
    except Exception as e:
        print("微博爬取错误：", e)
        return None
    finally:
        driver.quit()
