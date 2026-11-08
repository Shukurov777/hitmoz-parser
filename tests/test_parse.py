from pathlib import Path

from hitmoz.client import HitMoz, parse_page

HTML = (Path(__file__).parent / "fixture_top.html").read_text(encoding="utf-8")


def test_parse_page_fields():
    songs = parse_page(HTML, "https://example.com")
    assert len(songs) == 3
    s = songs[0]
    assert s["id"].isdigit()
    assert s["title"] and s["artist"]
    assert s["duration"].count(":") == 1 and s["seconds"] > 0
    assert s["download"].startswith("https://example.com/get/music/") and s["download"].endswith(".mp3")
    assert s["cover"].startswith("http")
    assert s["link"] == f"https://example.com/song/{s['id']}"


def test_build_dedup_and_rank():
    raw = parse_page(HTML, "https://example.com")
    songs = HitMoz._build([raw, raw], limit=10)
    assert [s.rank for s in songs] == [1, 2, 3]
