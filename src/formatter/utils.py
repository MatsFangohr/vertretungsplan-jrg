import datetime as dt
from collections.abc import Iterable
from typing import Literal

from utils import tz


def find_active_day(dates: Iterable[dt.date], now: dt.datetime) -> dt.date | None:
    """Find the active day based on the current time and the provided dates.


    The active day is determined based on the following rules:
    - If now is a weekend, return next available weekday.
    - If now is a weekday, return today if before 14:30, else tomorrow.
    - If tomorrow isn't an option, return today if it's in `dates`, else next available weekday.
    - If there are no available weekdays, return `None`."""
    sorted_dates = [d for d in sorted(dates) if d.weekday() <= 4]

    today = now.date()
    tomorrow = today + dt.timedelta(days=1)

    if today.weekday() in [5, 6]:
        return sorted_dates[0] if sorted_dates else None

    if (today in sorted_dates and tomorrow in sorted_dates) or today.weekday() == 4:
        if now > dt.datetime.combine(today, dt.time(14, 30), tzinfo=tz):
            return tomorrow
    elif today in sorted_dates:
        return today
    return sorted_dates[0] if sorted_dates else None


def get_color(klass: int, tone: Literal["pale", "dark"]) -> str:
    if tone not in ["pale", "dark"]:
        raise ValueError("unsupported color!")
    if tone == "pale":
        return f"var(--year-color-{klass})"
    else:  # tone must be dark
        return f"var(--year-color-{klass}-intense)"
