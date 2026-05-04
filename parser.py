#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер eu.hitmoz.com
Использование:
    python3 parser.py                  → топ сегодня
    python3 parser.py search "Jony"    → поиск
"""

import sys, json, re
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup

BASE_URL  = "https://eu.hitmoz.com"
STEP      = 48
PAGES     = 4

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.7",
    "Referer": BASE_URL + "/",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

DL_RE = re.compile(r"/get/music/.*\.mp3", re.I)


def error_out(msg):
    print(json.dumps({"success": False, "error": msg}, ensure_ascii=False, indent=2))
    sys.exit(1)


def fetch(url):
    try:
        r = SESSION.get(url, timeout=20)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except requests.RequestException as e:
        error_out(f"Ошибка: {e}")


def abs_url(href):
    if not href: return ""
    if href.startswith("http"): return href
    if href.startswith("//"): return "https:" + href
    return BASE_URL + href


def _normalize(src):
    src = src.strip()
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("http"):
        return src
    if src.startswith("/"):
        return BASE_URL + src
    return BASE_URL + "/" + src


def find_song_row(link_tag):
    """Поднимается по родителям пока не найдёт контейнер именно ЭТОГО трека."""
    row = link_tag
    for _ in range(8):
        if row.parent is None:
            break
        if len(row.parent.find_all("a", href=DL_RE)) > 1:
            return row
        row = row.parent
    return row


def extract_cover(row):
    """Ищет обложку всеми возможными способами."""
    if not row:
        return ""

    # 1. Все теги <img> в строке трека
    for img in row.find_all("img"):
        for attr in ["src", "data-src", "data-lazy-src", "data-original",
                     "data-bg", "data-image", "data-thumb"]:
            src = img.get(attr, "")
            if src and not src.startswith("data:"):
                return _normalize(src)

    # 2. background-image в style="..." у любого тега
    for el in row.find_all(True):
        style = el.get("style", "")
        if "background" in style:
            m = re.search(r'url\(["\']?([^"\')]+)["\']?\)', style)
            if m:
                return _normalize(m.group(1))

    # 3. data-* атрибуты с картинкой у любого тега
    for el in row.find_all(True):
        for attr_name, attr_val in el.attrs.items():
            if not isinstance(attr_val, str):
                continue
            if attr_name.startswith("data-") and re.search(r"\.(jpg|jpeg|png|webp)", attr_val, re.I):
                return _normalize(attr_val)

    # 4. Если не нашли — лезем в родителя
    if row.parent:
        for img in row.parent.find_all("img", limit=5):
            for attr in ["src", "data-src", "data-lazy-src", "data-original"]:
                src = img.get(attr, "")
                if src and not src.startswith("data:"):
                    return _normalize(src)

    return ""


def extract_song_data(row):
    """Из контейнера трека вытаскивает title, artist, duration, cover."""
    raw_texts = []
    for s in row.stripped_strings:
        s = s.strip()
        if not s or len(s) < 2:
            continue
        if s.lower() in ("скачать", "слушать", "play", "download", "хит", "★", "☆"):
            continue
        raw_texts.append(s)

    duration = ""
    content  = []
    for t in raw_texts:
        if re.fullmatch(r"\d{1,2}:\d{2}", t):
            duration = t
        else:
            content.append(t)

    title  = content[0] if len(content) >= 1 else ""
    artist = content[1] if len(content) >= 2 else ""
    cover  = extract_cover(row)

    return title, artist, duration, cover


def parse_filename(dl_url):
    """Запасной способ — артист и название из имени MP3 файла."""
    filename = dl_url.split("/")[-1].replace(".mp3", "")
    m = re.search(r"_(\d{6,})$", filename)
    song_id = m.group(1) if m else ""
    if m:
        filename = filename[:m.start()]
    if "_-_" in filename:
        parts  = filename.split("_-_", 1)
        artist = parts[0].replace("_", " ").strip()
        title  = parts[1].replace("_", " ").strip()
    else:
        artist, title = "", filename.replace("_", " ").strip()
    return artist, title, song_id


def parse_page(soup, rank_offset):
    songs = []
    seen  = set()

    for a in soup.find_all("a", href=DL_RE):
        href = abs_url(a.get("href", ""))
        if not href or href in seen:
            continue
        seen.add(href)

        row = find_song_row(a)
        title, artist, duration, cover = extract_song_data(row)

        # Fallback из имени файла
        f_artist, f_title, song_id = parse_filename(href)
        if not title:  title  = f_title
        if not artist: artist = f_artist

        songs.append({
            "rank":     rank_offset + len(songs) + 1,
            "title":    title,
            "artist":   artist,
            "duration": duration,
            "cover":    cover,
            "download": href,
            "link":     f"{BASE_URL}/song/{song_id}" if song_id else "",
        })

    return songs


def parse_top_today():
    """Топ сегодня — 4 страницы по 48 треков."""
    start_url  = BASE_URL + "/songs/top-today"
    pages_urls = [start_url] + [f"{start_url}/start/{STEP*i}" for i in range(1, PAGES)]

    all_songs = []
    for url in pages_urls:
        soup = fetch(url)
        all_songs.extend(parse_page(soup, len(all_songs)))

    return {
        "success": True,
        "mode":    "top-today",
        "source":  start_url,
        "count":   len(all_songs),
        "songs":   all_songs,
    }


def parse_search(query):
    """Поиск по запросу с пагинацией."""
    base = f"{BASE_URL}/search?q={quote_plus(query)}"
    urls = [base] + [f"{base}&start={STEP*i}" for i in range(1, PAGES)]

    all_songs = []
    seen_dl   = set()

    for url in urls:
        soup      = fetch(url)
        new_songs = parse_page(soup, len(all_songs))

        before = len(all_songs)
        for s in new_songs:
            if s["download"] in seen_dl:
                continue
            seen_dl.add(s["download"])
            s["rank"] = len(all_songs) + 1
            all_songs.append(s)

        if len(all_songs) == before:
            break  # больше нет результатов

    return {
        "success": True,
        "mode":    "search",
        "query":   query,
        "source":  base,
        "count":   len(all_songs),
        "songs":   all_songs,
    }


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        query = sys.argv[2].strip()
        if not query:
            error_out("Пустой поисковый запрос")
        result = parse_search(query)
    else:
        result = parse_top_today()

    if not result["songs"]:
        if result.get("mode") == "search":
            error_out(f"По запросу «{result.get('query')}» ничего не найдено")
        error_out("Треки не найдены")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
