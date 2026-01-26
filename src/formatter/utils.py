import datetime as dt
from typing import Literal

import utils
from utils import tz


def find_active_day(dates: list[dt.date]) -> dt.date:
    today = utils.today()
    tomorrow = today + dt.timedelta(days=1)

    if (today in dates and tomorrow in dates) or today.weekday() == 4:  # noqa: SIM102
        if utils.now() > dt.datetime.combine(today, dt.time(14, 30), tzinfo=tz):
            return tomorrow
    return today


def get_color(klass: int, tone: Literal["pale", "dark", "normal", "strong"]) -> str:
    if tone not in ["pale", "dark"]:
        raise ValueError("unsupported color!")
    if tone == "pale":
        return f"var(--year-color-{klass})"
    else:  # tone must be dark
        return f"var(--year-color-{klass}-intense)"
