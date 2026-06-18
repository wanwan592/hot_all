# spiders/ithome.py
import requests
import parsel
import time

def get_ithome_hot():
    """获取IT之家首页热门文章，返回 [(标题, 链接), ...]"""
    url = "https://www.ithome.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://www.ithome.com/"
    }
    max_retries = 3
    resp = None
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.encoding = "utf-8"
            break
        except Exception as e:
            print(f"IT之家连接失败 (第 {attempt+1}/{max_retries} 次): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(2)

    if resp is None:
        return None

    sel = parsel.Selector(resp.text)

    selectors = [
        '#news_list .news-item a',
        '.news-item a',
        '.list-item a',
        '.news-list a',
        '.post-item a'
    ]
    items = None
    for sel_str in selectors:
        items = sel.css(sel_str)
        if items:
            break

    if not items:
        print("IT之家：未找到标准列表，使用通用过滤方案")
        all_a = sel.css('a[href^="/"]')
        exclude_keywords = [
            '立即下载', '系统镜像', '固件下载', '描述文件', '喜加一', '限免',
            '工具', '导航', 'RSS', 'App客户端', '查看更多', '客户端', '订阅',
            '手机客户端', '下载'
        ]
        items = []
        for a in all_a:
            href = a.attrib.get('href', '')
            title = a.css('::text').get()
            if not title or not href:
                continue
            title = title.strip()
            if len(title) < 5 or any(kw in title for kw in exclude_keywords):
                continue
            if any(bad in href for bad in ['rss', 'labs', 'm.ruanmei.com', '/d/it', '/zt/', '/tag/', '/about']):
                continue
            if not (href.count('/') >= 3 and ('.htm' in href or href.count('/') >= 4)):
                continue
            items.append(a)

    links, titles = [], []
    for a in items:
        href = a.attrib.get('href', '')
        title = a.css('::text').get()
        if not title or not href:
            continue
        title = title.strip()
        if not title or len(title) < 4:
            continue
        if href.startswith('//'):
            href = 'https:' + href
        elif href.startswith('/'):
            href = 'https://www.ithome.com' + href
        links.append(href)
        titles.append(title)
        if len(links) >= 20:
            break

    seen = set()
    result = []
    for t, l in zip(titles, links):
        if l in seen:
            continue
        seen.add(l)
        result.append((t, l))
        if len(result) >= 15:
            break

    return result
