from __future__ import annotations

import argparse
import asyncio
import json
import sys


def _print(res, as_json: bool) -> None:
    if as_json or not sys.stdout.isatty():
        print(json.dumps(res.to_dict(), ensure_ascii=False, indent=2))
        return
    for s in res.songs:
        print(f"{s.rank:>3}. {s.artist} — {s.title}  [{s.duration}]")
        print(f"     {s.download}")
    print(f"\n{res.count} tracks · {res.took_ms} ms")


def main() -> None:
    p = argparse.ArgumentParser(prog="hitmoz", description="HitMoz music: chart, search, REST API, MCP")
    sub = p.add_subparsers(dest="cmd")
    t = sub.add_parser("top", help="today's chart")
    t.add_argument("-n", "--limit", type=int, default=50)
    t.add_argument("--json", action="store_true")
    s = sub.add_parser("search", help="search tracks")
    s.add_argument("query", nargs="+")
    s.add_argument("-n", "--limit", type=int, default=48)
    s.add_argument("--json", action="store_true")
    sv = sub.add_parser("serve", help="run REST API (needs `pip install hitmoz[server]`)")
    sv.add_argument("--host", default="0.0.0.0")
    sv.add_argument("--port", type=int, default=8000)
    sv.add_argument("--workers", type=int, default=1)
    sub.add_parser("mcp", help="run MCP server for AI agents (needs `pip install hitmoz[mcp]`)")
    a = p.parse_args()

    if a.cmd == "serve":
        import uvicorn

        uvicorn.run("hitmoz.api:app", host=a.host, port=a.port, workers=a.workers, log_level="info")
        return
    if a.cmd == "mcp":
        from .mcp_server import run

        run()
        return

    from .client import HitMoz

    async def go():
        async with HitMoz() as hm:
            if a.cmd == "search":
                return await hm.search(" ".join(a.query), a.limit)
            return await hm.top(getattr(a, "limit", 50))

    try:
        res = asyncio.run(go())
    except (ConnectionError, ValueError) as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)
    _print(res, getattr(a, "json", False))
