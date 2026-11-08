<div align="center">

# 🎵 HitMoz

**Blazing fast music API — today's chart and search with direct MP3 links.**

Async Python client · REST API · CLI · Docker · MCP server for AI agents

[![Live API](https://img.shields.io/badge/live_API-bakha.me%2Fhitmoz-000000?style=for-the-badge)](https://bakha.me/hitmoz/docs)
[![Python](https://img.shields.io/badge/python-3.10+-000000?style=for-the-badge&logo=python&logoColor=white)](#-python)
[![Docker](https://img.shields.io/badge/docker-ready-000000?style=for-the-badge&logo=docker&logoColor=white)](#-docker)
[![License](https://img.shields.io/badge/license-MIT-000000?style=for-the-badge)](LICENSE)

</div>

```bash
curl "https://bakha.me/hitmoz/search?q=Jony&limit=1"
```
```json
{
  "success": true, "mode": "search", "query": "Jony", "count": 1, "cached": false, "took_ms": 393,
  "songs": [{
    "rank": 1, "id": "82169781", "title": "Журавли", "artist": "Клава Кока, JONY",
    "duration": "03:18", "seconds": 198,
    "cover": "https://statcore.hitmcdn.com/cover/...jpg",
    "download": "https://ru.hitmox.com/get/music/20260924/..._82169781.mp3",
    "stream": "https://ru.hitmox.com/get/cuts/.../82169781/...mp3",
    "link": "https://ru.hitmox.com/song/82169781"
  }]
}
```

## ⚡ Speed

| | v1 (requests + BeautifulSoup) | **v2** |
|---|---|---|
| Chart, 192 tracks | 2.2 s | **0.7 s** (parallel pages over HTTP/2) |
| Repeated request | 2.2 s | **< 0.1 ms** (in-memory cache) |
| Public API `/top` | — | **~40 ms** (always warm) |
| Parsing one page | ~150 ms (DOM) | **~1 ms** (precompiled regex on embedded JSON) |

How: one keep-alive HTTP/2 connection, all pages fetched concurrently, no DOM building, TTL cache,
identical concurrent requests coalesced into one, background chart refresh in the API.

## 🌍 Connect from anywhere

| Way | For | |
|---|---|---|
| **Public REST API** | any language, browser, bots, no install | [`https://bakha.me/hitmoz`](https://bakha.me/hitmoz/docs) |
| **pip** | Python apps & bots | `pip install git+https://github.com/Shukurov777/hitmoz-parser` |
| **Docker** | your own server | `docker compose up -d` |
| **CLI** | terminal, scripts | `hitmoz top`, `hitmoz search "Jony"` |
| **MCP** | Claude, Cursor & other AI agents | `hitmoz mcp` |

Mirror failover is built in (`eu.hitmoz.com → ru.hitmox.com → …`): if the site moves, the client follows.
If it's blocked in your country — set `HITMOZ_PROXY=socks5://…`.

## 🌐 REST API

Interactive docs: **[bakha.me/hitmoz/docs](https://bakha.me/hitmoz/docs)**

| Endpoint | Description |
|---|---|
| `GET /top?limit=100` | Today's chart, up to 500 tracks |
| `GET /search?q=Jony&limit=48` | Search by artist or title, up to 400 tracks |
| `GET /health` | Status and current mirror |

CORS is open, responses are gzipped and cacheable. `index.php?top-today` and `index.php?search=` from v1 still work.

```js
const { songs } = await (await fetch("https://bakha.me/hitmoz/top?limit=10")).json();
```
```php
$data = json_decode(file_get_contents('https://bakha.me/hitmoz/search?q=' . urlencode('ЕГОР КРИД')), true);
```

## 🐍 Python

```bash
pip install git+https://github.com/Shukurov777/hitmoz-parser                       # client + CLI
pip install "hitmoz[server] @ git+https://github.com/Shukurov777/hitmoz-parser"   # + REST API
```

```python
import asyncio
from hitmoz import HitMoz

async def main():
    async with HitMoz() as hm:
        chart, found = await asyncio.gather(hm.top(10), hm.search("Мальборо"))
        for s in chart.songs:
            print(s.rank, s.artist, "—", s.title, s.download)

asyncio.run(main())
```

Blocking code? `from hitmoz.client import top, search; search("Jony").songs`

## 💻 CLI

```bash
hitmoz top -n 20               # pretty list in terminal
hitmoz search "ЕГОР КРИД"
hitmoz top --json > top.json   # JSON (also automatic when piped)
hitmoz serve --port 8000       # REST API
```

## 🐳 Docker

```bash
docker compose up -d           # → http://localhost:8000/docs
# or
docker run -p 8000:8000 ghcr.io/shukurov777/hitmoz
```

## 🤖 MCP (AI agents)

```bash
pip install "hitmoz[mcp] @ git+https://github.com/Shukurov777/hitmoz-parser"
claude mcp add hitmoz -- hitmoz mcp
```

Tools: `search_music`, `top_chart`. Then just ask: *"find 5 tracks by JONY and give me download links"*.

## ⚙️ Settings

| Env | Default | |
|---|---|---|
| `HITMOZ_CACHE_TTL` | `600` | Cache lifetime, seconds (`0` = off) |
| `HITMOZ_PROXY` | — | `http://…` or `socks5://…` |
| `HITMOZ_MIRRORS` | built-in list | Comma-separated base URLs |
| `HITMOZ_ROOT_PATH` | — | URL prefix when served behind a proxy (`/hitmoz`) |

## 📁 Examples

[`examples/`](examples) — JavaScript, PHP, async Python and a **20-line Telegram music bot**.

## ⚠️ Disclaimer

For educational purposes. All music belongs to its rights holders. Respect the source site's terms and
don't hammer it — the built-in cache exists for a reason.

## License

[MIT](LICENSE) © Bahrullo Shukurov · If it saved you time — **⭐ the repo**.
