# spiders/baidu.py
import requests
from lxml import etree

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/133.0.0.0 Safari/537.36"
API_URL = "https://top.baidu.com/api/board?platform=wise&tab=realtime"


def _fetch_via_api():
    """方案一：官方榜单 API，返回稳定的 JSON 结构"""
    headers = {"User-Agent": UA, "Referer": "https://top.baidu.com/"}
    resp = requests.get(API_URL, headers=headers, timeout=10)
    resp.encoding = "utf-8"
    data = resp.json()
    cards = data.get("data", {}).get("cards", [])
    if not cards:
        return None
    # 结构：cards[0].content 可能是列表，其元素的 content 才是热搜条目
    entries = []
    for card in cards:
        content = card.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and isinstance(block.get("content"), list):
                    entries.extend(block["content"])
                elif isinstance(block, dict) and block.get("word"):
                    entries.append(block)
    result = []
    for item in entries:
        word = (item.get("word") or "").strip()
        if word and word not in result:
            result.append(word)
    return result or None


def _fetch_via_html():
    """方案二（兜底）：解析百度首页 HTML"""
    res = requests.get("https://www.baidu.com/", headers={"user-agent": UA}, timeout=10)
    res.encoding = "utf-8"
    html = etree.HTML(res.text)
    xpaths = [
        '//*[@id="hotsearch-content-wrapper"]/li/a/span[@class="title-content-title"]/text()',
        '//div[@id="hotsearch-content-wrapper"]//a/span[@class="title-content-title"]/text()',
        '//div[contains(@class, "hotsearch")]//a/span[contains(@class, "title")]/text()',
        '//div[contains(@class, "hot-list")]//a/text()',
    ]
    for xp in xpaths:
        lst = html.xpath(xp)
        if lst:
            return lst
    return None


def get_baidu_hot():
    """获取百度热搜列表（仅标题），API 优先、HTML 兜底，返回列表或 None"""
    try:
        result = _fetch_via_api()
        if result:
            return result
    except Exception as e:
        print(f"百度 API 爬取错误：{e}")
    try:
        return _fetch_via_html()
    except Exception as e:
        print(f"百度 HTML 爬取错误：{e}")
        return None
