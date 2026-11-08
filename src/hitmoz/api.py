"""REST API: `hitmoz serve` or `uvicorn hitmoz.api:app`."""

from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, RedirectResponse

from . import __version__
from .client import HitMoz

hm: HitMoz | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global hm
    hm = HitMoz()

    async def keep_warm():
        # refresh the chart before it expires, so /top is always answered from memory
        while True:
            try:
                hm._cache = {k: v for k, v in hm._cache.items() if not k.startswith("top:")}
                await hm.top(192)
            except Exception:
                pass
            await asyncio.sleep(max(60, hm.cache_ttl - 60))

    task = asyncio.create_task(keep_warm())
    yield
    task.cancel()
    await hm.close()


app = FastAPI(
    title="HitMoz API",
    version=__version__,
    description="Fast JSON API for the HitMoz music catalog: today's chart and search with direct MP3 links.",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    root_path=os.getenv("HITMOZ_ROOT_PATH", ""),
)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])


def _cache_headers(resp: Response, seconds: int = 300) -> None:
    resp.headers["Cache-Control"] = f"public, max-age={seconds}, stale-while-revalidate=600"


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(app.root_path + "/docs")


@app.get("/health", tags=["service"])
async def health():
    return {"ok": True, "version": __version__, "mirror": hm.base if hm else None}


@app.get("/top", tags=["music"], summary="Today's chart")
async def top(response: Response, limit: int = Query(100, ge=1, le=500)):
    try:
        res = await hm.top(limit)
    except ConnectionError as e:
        raise HTTPException(502, str(e))
    _cache_headers(response)
    return res.to_dict()


@app.get("/search", tags=["music"], summary="Search tracks by artist or title")
async def search(response: Response, q: str = Query(..., min_length=1, max_length=200), limit: int = Query(48, ge=1, le=400)):
    try:
        res = await hm.search(q, limit)
    except ConnectionError as e:
        raise HTTPException(502, str(e))
    if not res.songs:
        return ORJSONResponse({"success": False, "query": q, "error": "Nothing found", "songs": []}, status_code=404)
    _cache_headers(response, 1800)
    return res.to_dict()


# backwards compatibility with v1 (index.php?top-today / index.php?search=)
@app.get("/index.php", include_in_schema=False)
async def legacy(response: Response, search: str | None = None):
    if search:
        return await globals()["search"](response, q=search, limit=192)
    return await top(response, limit=192)
