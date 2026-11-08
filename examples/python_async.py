import asyncio

from hitmoz import HitMoz


async def main():
    async with HitMoz() as hm:
        chart, found = await asyncio.gather(hm.top(10), hm.search("Мальборо", limit=5))
        for s in chart.songs:
            print(s.rank, s.artist, "—", s.title, s.download)
        print(f"\nsearch: {found.count} tracks in {found.took_ms} ms")


asyncio.run(main())
