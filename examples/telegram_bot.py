"""Minimal music bot: send an artist or a title, get MP3 files back.
pip install hitmoz aiogram  ·  BOT_TOKEN=... python telegram_bot.py
"""
import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

from hitmoz import HitMoz

bot, dp, hm = Bot(os.environ["BOT_TOKEN"]), Dispatcher(), HitMoz()


@dp.message(F.text)
async def find(m: Message):
    res = await hm.search(m.text, limit=3)
    if not res.songs:
        return await m.answer("Nothing found 🤷")
    for s in res.songs:
        await m.answer_audio(s.download, title=s.title, performer=s.artist, duration=s.seconds)


asyncio.run(dp.start_polling(bot))
