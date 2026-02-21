import datetime as dt
from typing import Literal

import utils
from utils import tz


def find_active_day(dates: list[dt.date]) -> dt.date:
    """Using current date and time, determines which date should be shown on page load from the
    given options.

    Will return `dates[0]` if today is a weekend, sorting `dates` ascendingly is recommended
    accordingly.
    """
    today = utils.today()
    tomorrow = today + dt.timedelta(days=1)

    if today.weekday() in [5, 6]:
        return dates[0]

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
