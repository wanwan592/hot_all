# spiders/github.py
import os
import re
import sys
import json
import time
import threading
import datetime
import concurrent.futures
from urllib.parse import quote

import requests
import urllib3
import parsel

# 部分网络环境（如代理）会导致 GitHub 证书链验证失败，降级请求时会产生大量警告
urllib3.disable_warnings()

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
TRENDING_URL = "https://github.com/trending?since=weekly"
API_URL = "https://api.github.com/search/repositories"
# 带 de 邮箱参数可显著提升 MyMemory 免费额度，避免触发 429 限额
TRANSLATE_URL = "https://api.mymemory.translated.net/get?langpair=en|zh-CN&de=hotsearch2026@gmail.com&q="

# 翻译缓存：内存 + 磁盘。磁盘缓存跨进程保留，彻底避免重启后重复翻译耗尽额度
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CACHE_FILE = os.path.join(_BASE_DIR, 'trans_cache.json')


def _load_cache():
    try:
        if os.path.exists(_CACHE_FILE):
            with open(_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


_TRANS_CACHE = _load_cache()
_CACHE_LOCK = threading.Lock()
_HAS_CJK = re.compile(r'[\u4e00-\u9fff]')


def _save_cache():
    try:
        with open(_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(_TRANS_CACHE, f, ensure_ascii=False)
    except Exception:
        pass


def _request(url, headers, timeout=20, retries=3):
    """请求封装：先正常验证证书，失败自动降级 verify=False；带递增退避"""
    last_err = None
    for attempt in range(retries):
        for verify in (True, False):
            try:
                resp = requests.get(url, headers=headers, timeout=timeout, verify=verify)
                if resp.status_code == 200:
                    return resp
                last_err = f"HTTP {resp.status_code}"
            except requests.exceptions.SSLError as e:
                last_err = f"SSLError(verify={verify}): {e}"
                continue  # 换 verify=False 再试
            except Exception as e:
                last_err = f"{type(e).__name__}: {e}"
        if attempt < retries - 1:
            time.sleep(1.5 * (attempt + 1))
    print(f"GitHub 请求失败: {last_err}")
    return None


def _translate(text, timeout=10):
    """把英文翻译成中文（MyMemory 免费接口），失败保留原文；带内存缓存"""
    text = (text or '').strip()
    if not text or _HAS_CJK.search(text):
        return text
    # MyMemory 对单次请求有长度限制，截断到词边界
    if len(text) > 400:
        text = text[:400].rsplit(' ', 1)[0] + '...'
    with _CACHE_LOCK:
        if text in _TRANS_CACHE:
            return _TRANS_CACHE[text]
    try:
        resp = requests.get(TRANSLATE_URL + quote(text),
                            headers={"User-Agent": UA}, timeout=timeout, verify=False)
        data = resp.json().get('responseData', {})
        cn = (data.get('translatedText') or '').strip()
        # 限额告警或空结果都视为翻译失败
        if cn and 'MYMEMORY WARNING' not in cn.upper() and 'QUERY LENGTH LIMIT' not in cn.upper():
            with _CACHE_LOCK:
                _TRANS_CACHE[text] = cn
                _save_cache()  # 立即落盘，重启后仍可命中
            return cn
    except Exception:
        pass
    return text  # 翻译失败回退英文原文，不影响主流程


def _localize_titles(result):
    """批量把标题里 ' · ' 之后的项目描述翻译成中文（并发以缩短耗时）"""
    if not result:
        return result

    def one(item):
        title, link = item
        parts = title.split('  ·  ', 1)
        if len(parts) == 2 and parts[1].strip():
            cn = _translate(parts[1])
            if cn != parts[1]:
                return (parts[0] + '  ·  ' + cn, link)
        return item

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        return list(pool.map(one, result))


def _normalize_week_text(text):
    """把 '2,395 stars this week' 规整为 '+2,395/周'"""
    m = re.search(r'([\d,]+)', text or '')
    return f"+{m.group(1)}/周" if m else ""


def _fetch_via_trending():
    """方案一：GitHub Trending 周榜页面（本周新增 star 最多）"""
    resp = _request(TRENDING_URL, {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    if resp is None:
        return None
    resp.encoding = "utf-8"
    sel = parsel.Selector(resp.text)
    result = []
    seen = set()
    for row in sel.css('article.Box-row'):
        href = row.css('h2 a::attr(href)').get()
        if not href or href in seen:
            continue
        full_name = href.strip('/')
        if full_name.count('/') != 1:
            continue
        seen.add(href)
        desc = ' '.join(t.strip() for t in row.css('p::text').getall() if t.strip())
        week_raw = ' '.join(t.strip() for t in row.css('span.d-inline-block.float-sm-right::text').getall())
        week = _normalize_week_text(week_raw)
        title = full_name
        if week:
            title += f"  {week}"
        if desc:
            title += f"  ·  {desc}"
        link = "https://github.com" + href if href.startswith('/') else href
        result.append((title.strip(), link))
        if len(result) >= 15:
            break
    return result or None


def _fetch_via_api():
    """方案二（兜底）：GitHub 官方 Search API，取最近 7 天新建且 star 最多的项目"""
    since = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    url = f"{API_URL}?q=created:%3E{since}&sort=stars&order=desc&per_page=15"
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    resp = _request(url, headers, timeout=20, retries=2)
    if resp is None:
        return None
    try:
        items = resp.json().get('items', [])
    except Exception as e:
        print(f"GitHub API 解析失败: {e}")
        return None
    result = []
    for it in items:
        full_name = it.get('full_name', '')
        if not full_name:
            continue
        stars = it.get('stargazers_count') or 0
        desc = (it.get('description') or '').strip()
        title = f"{full_name}  ★{stars:,}（近7天新项目）"
        if desc:
            title += f"  ·  {desc}"
        result.append((title.strip(), it.get('html_url', f"https://github.com/{full_name}")))
    return result or None


def get_github_weekly():
    """获取 GitHub 本周热门项目（中文描述）：Trending 优先，官方 API 兜底"""
    result = _fetch_via_trending()
    if result:
        return _localize_titles(result)
    print("GitHub Trending 不可用，回退官方 Search API")
    result = _fetch_via_api()
    return _localize_titles(result) if result else None
