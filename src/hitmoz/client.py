"""Async HitMoz client.

* parallel page fetching over one keep-alive HTTP/2 connection
* parsing with precompiled regexes (no DOM, ~1 ms per page)
* automatic mirror discovery + failover (eu.hitmoz.com, ru.hitmox.com, ...)
* in-memory TTL cache with request coalescing
"""

from __future__ import annotations

import asyncio
import html
import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.parse import quote_plus

import httpx

PAGE_SIZE = 48
DEFAULT_MIRRORS = ("https://eu.hitmoz.com", "https://ru.hitmox.com", "https://hitmoz.com", "https://hitmo.me")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}

_ITEM = re.compile(r'<li class="tracks__item[^"]*"[^>]*?data-musmeta=\'([^\']+)\'(.*?)</li>', re.S)
_TIME = re.compile(r'track__fulltime">\s*([\d:]+)')
_DL = re.compile(r'href="(/get/music/[^"]+\.mp3)"')
_LAST_PAGE = re.compile(r'/start/(\d+)')


@dataclass(slots=True)
class Song:
    rank: int
    id: str
    title: str
    artist: str
    duration: str
    seconds: int
    cover: str
    download: str
    stream: str
    link: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Result:
    mode: str
    source: str
    songs: list[Song] = field(default_factory=list)
    query: str | None = None
    cached: bool = False
    took_ms: int = 0

    @property
    def count(self) -> int:
        return len(self.songs)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"success": True, "mode": self.mode}
        if self.query is not None:
            d["query"] = self.query
        d.update(
            source=self.source,
            count=self.count,
            cached=self.cached,
            took_ms=self.took_ms,
            songs=[s.to_dict() for s in self.songs],
        )
        return d


def _secs(t: str) -> int:
    try:
        parts = [int(x) for x in t.split(":")]
    except ValueError:
        return 0
    total = 0
    for p in parts:
        total = total * 60 + p
    return total


def parse_page(page: str, base: str) -> list[dict[str, Any]]:
    """Extract tracks from one HTML page. Pure function, very fast."""
    out = []
    for meta_raw, body in _ITEM.findall(page):
        try:
            meta = json.loads(html.unescape(meta_raw))
        except ValueError:
            continue
        sid = str(meta.get("id", "")).replace("track-id-", "")
        dl = _DL.search(body)
        tm = _TIME.search(body)
        duration = tm.group(1) if tm else ""
        out.append(
            {
                "id": sid,
                "title": (meta.get("title") or "").strip(),
                "artist": (meta.get("artist") or "").strip(),
                "duration": duration,
                "seconds": _secs(duration),
                "cover": meta.get("img") or "",
                "download": base + dl.group(1) if dl else meta.get("url", ""),
                "stream": meta.get("url") or "",
                "link": f"{base}/song/{sid}" if sid else "",
            }
        )
    return out


class HitMoz:
    """Async client. Use as `async with HitMoz() as hm:` or keep one instance for the app lifetime."""

    def __init__(
        self,
        mirrors: tuple[str, ...] | list[str] | None = None,
        proxy: str | None = None,
        timeout: float = 12.0,
        cache_ttl: int = 600,
        concurrency: int = 8,
    ) -> None:
        env = os.getenv("HITMOZ_MIRRORS")
        self.mirrors = list(mirrors or (env.split(",") if env else DEFAULT_MIRRORS))
        self.base = self.mirrors[0].rstrip("/")
        self._resolved = False
        self.cache_ttl = int(os.getenv("HITMOZ_CACHE_TTL", cache_ttl))
        self._sem = asyncio.Semaphore(concurrency)
        self._cache: dict[str, tuple[float, Result]] = {}
        self._inflight: dict[str, asyncio.Future] = {}
        try:
            import h2  # noqa: F401

            http2 = True
        except ImportError:
            http2 = False
        self._http = httpx.AsyncClient(
            headers=HEADERS,
            http2=http2,
            follow_redirects=True,
            timeout=httpx.Timeout(timeout, connect=5.0),
            proxy=proxy or os.getenv("HITMOZ_PROXY") or None,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10, keepalive_expiry=60),
        )

    async def __aenter__(self) -> "HitMoz":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

    async def close(self) -> None:
        await self._http.aclose()

    # ------------------------------------------------------------------ http

    async def _get(self, path: str) -> str:
        """GET with mirror failover. Remembers the mirror that answered (after redirects)."""
        order = [self.base] + [m.rstrip("/") for m in self.mirrors if m.rstrip("/") != self.base]
        last: Exception | None = None
        for base in order:
            try:
                async with self._sem:
                    r = await self._http.get(base + path)
                if r.status_code == 200 and "<html" in r.text[:3000].lower():
                    self.base = f"{r.url.scheme}://{r.url.host}"
                    return r.text
                last = httpx.HTTPStatusError(f"{r.status_code} from {base}", request=r.request, response=r)
            except httpx.HTTPError as e:
                last = e
            self._resolved = False
        raise ConnectionError(f"All mirrors failed: {last}")

    async def _pages(self, paths: list[str]) -> list[str]:
        if not self._resolved:  # first call discovers the live mirror, then everything goes in parallel
            first = await self._get(paths[0])
            self._resolved = True
            rest = await asyncio.gather(*(self._get(p) for p in paths[1:]), return_exceptions=True)
            return [first] + [x for x in rest if isinstance(x, str)]
        got = await asyncio.gather(*(self._get(p) for p in paths), return_exceptions=True)
        if not isinstance(got[0], str):
            raise got[0]
        return [x for x in got if isinstance(x, str)]

    # ------------------------------------------------------------------ cache

    async def _cached(self, key: str, factory) -> Result:
        hit = self._cache.get(key)
        if hit and hit[0] > time.monotonic():
            res = hit[1]
            return Result(res.mode, res.source, res.songs, res.query, cached=True, took_ms=0)
        if key in self._inflight:  # coalesce identical concurrent requests
            return await asyncio.shield(self._inflight[key])
        fut = asyncio.get_running_loop().create_future()
        self._inflight[key] = fut
        try:
            t = time.perf_counter()
            res = await factory()
            res.took_ms = int((time.perf_counter() - t) * 1000)
            if res.songs and self.cache_ttl > 0:
                self._cache[key] = (time.monotonic() + self.cache_ttl, res)
            fut.set_result(res)
            return res
        except Exception as e:
            fut.set_exception(e)
            fut.exception()  # mark retrieved
            raise
        finally:
            self._inflight.pop(key, None)

    # ------------------------------------------------------------------ public api

    @staticmethod
    def _build(raw_pages: list[list[dict]], limit: int) -> list[Song]:
        seen, songs = set(), []
        for page in raw_pages:
            for s in page:
                key = s["id"] or s["download"]
                if key in seen:
                    continue
                seen.add(key)
                songs.append(Song(rank=len(songs) + 1, **s))
                if len(songs) >= limit:
                    return songs
        return songs

    async def top(self, limit: int = 100) -> Result:
        """Today's chart. limit up to ~500."""
        limit = max(1, min(limit, 500))
        pages = -(-limit // PAGE_SIZE)

        async def run() -> Result:
            paths = ["/songs/top-today"] + [f"/songs/top-today/start/{PAGE_SIZE * i}" for i in range(1, pages)]
            html_pages = await self._pages(paths)
            raw = [parse_page(p, self.base) for p in html_pages]
            return Result("top-today", self.base + "/songs/top-today", self._build(raw, pages * PAGE_SIZE))

        # any fresh chart that is big enough answers smaller requests instantly
        now = time.monotonic()
        for key, (exp, res) in list(self._cache.items()):
            if key.startswith("top:") and exp > now and res.count >= limit:
                return Result(res.mode, res.source, res.songs[:limit], cached=True)
        res = await self._cached(f"top:{pages * PAGE_SIZE}", run)
        if res.count > limit:
            res = Result(res.mode, res.source, res.songs[:limit], cached=res.cached, took_ms=res.took_ms)
        return res

    async def search(self, query: str, limit: int = 48) -> Result:
        """Search by artist or title. limit up to ~400."""
        query = query.strip()
        if not query:
            raise ValueError("Empty query")
        limit = max(1, min(limit, 400))
        q = quote_plus(query)

        async def run() -> Result:
            first = await self._get(f"/search?q={q}")
            raw = [parse_page(first, self.base)]
            starts = [int(x) for x in _LAST_PAGE.findall(first)]
            last = max(starts, default=0)
            want = min(last // PAGE_SIZE + 1, -(-limit // PAGE_SIZE))
            if want > 1 and raw[0]:
                more = await asyncio.gather(
                    *(self._get(f"/search/start/{PAGE_SIZE * i}?q={q}") for i in range(1, want)),
                    return_exceptions=True,
                )
                raw += [parse_page(p, self.base) for p in more if isinstance(p, str)]
            return Result("search", f"{self.base}/search?q={q}", self._build(raw, limit), query=query)

        return await self._cached(f"search:{query.lower()}:{limit}", run)


# ---------------------------------------------------------------------- sync helpers


def top(limit: int = 100) -> Result:
    """Blocking helper: `hitmoz.client.top()`."""

    async def run():
        async with HitMoz() as hm:
            return await hm.top(limit)

    return asyncio.run(run())


def search(query: str, limit: int = 48) -> Result:
    """Blocking helper: `hitmoz.client.search("Jony")`."""

    async def run():
        async with HitMoz() as hm:
            return await hm.search(query, limit)

    return asyncio.run(run())
