# spiders/baidu.py
import requests
from lxml import etree

def get_baidu_hot():
    """获取百度热搜列表（仅标题）"""
    url = "https://www.baidu.com/"
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/133.0.0.0 Safari/537.36"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        html = etree.HTML(res.text)
        xpaths = [
            '//*[@id="hotsearch-content-wrapper"]/li/a/span[@class="title-content-title"]/text()',
            '//div[@id="hotsearch-content-wrapper"]//a/span[@class="title-content-title"]/text()',
            '//div[contains(@class, "hotsearch")]//a/span[contains(@class, "title")]/text()',
            '//div[contains(@class, "hot-list")]//a/text()',
        ]
        lst = None
        for xp in xpaths:
            lst = html.xpath(xp)
            if lst:
                break
        return lst if lst else []
    except Exception as e:
        print("百度爬取错误：", e)
        return None
