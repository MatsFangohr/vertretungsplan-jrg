from __future__ import annotations

import asyncio
import datetime as dt

import aiohttp

import config
from logger import info
from untis.data import BASE_PAYLOAD
from untis.raw_types import PackedRawWebUntisData


class WebUntisManager:
    """
    Manager for fetching data from WebUntis.
    Uses aiohttp to make asynchronous requests to the WebUntis API.
    Call `get_raw_untis_data` to use.
    """

    async def get_data(
        self, session: aiohttp.ClientSession, date: dt.date
    ) -> PackedRawWebUntisData:
        payload = {"date": int(date.strftime("%Y%m%d"))} | BASE_PAYLOAD
        async with session.post(config.api_url, json=payload) as r:
            return await r.json()

    async def get_multiple(self, dates: list[dt.date]) -> dict[dt.date, PackedRawWebUntisData]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_data(session, d) for d in dates]
            results = await asyncio.gather(*tasks)
        return dict(zip(dates, results, strict=True))

    @classmethod
    def get_raw_untis_data(cls, dates: list[dt.date]) -> dict[dt.date, PackedRawWebUntisData]:
        info("contacting webuntis...")
        return asyncio.run(cls().get_multiple(dates))
