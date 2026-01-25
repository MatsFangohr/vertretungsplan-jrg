from __future__ import annotations

import asyncio
import datetime as dt

import aiohttp

from untis.data import BASE_PAYLOAD
from untis.raw_types import RawWebUntisData


class WebUntisManager:
    url: str

    def __init__(self) -> None:
        self.url = (
            "https://rist2024.webuntis.com/WebUntis/monitor/substitution/data?school=rist2024"
        )

    async def get_data(self, session: aiohttp.ClientSession, date: dt.date) -> RawWebUntisData:
        payload = {"date": int(date.strftime("%Y%m%d"))} | BASE_PAYLOAD
        async with session.post(self.url, json=payload) as r:
            return (await r.json())["payload"]

    async def get_multiple(self, dates: list[dt.date]) -> dict[dt.date, RawWebUntisData]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_data(session, d) for d in dates]
            results = await asyncio.gather(*tasks)
        return dict(zip(dates, results, strict=True))
