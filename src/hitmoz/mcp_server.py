"""MCP server so Claude / Cursor / any AI agent can search music."""

from __future__ import annotations

try:  # mcp >= 2
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

from .client import HitMoz

mcp = _Server("hitmoz", instructions="Search music and get today's chart with direct MP3 download links.")
_hm: HitMoz | None = None


def _client() -> HitMoz:
    global _hm
    if _hm is None:
        _hm = HitMoz()
    return _hm


def _fmt(res) -> str:
    return "\n".join(f"{s.rank}. {s.artist} — {s.title} [{s.duration}] {s.download}" for s in res.songs) or "Nothing found."


@mcp.tool()
async def search_music(query: str, limit: int = 10) -> str:
    """Search tracks by artist or title. Returns direct MP3 links."""
    return _fmt(await _client().search(query, limit))


@mcp.tool()
async def top_chart(limit: int = 20) -> str:
    """Today's most popular tracks with direct MP3 links."""
    return _fmt(await _client().top(limit))


def run() -> None:
    mcp.run()
