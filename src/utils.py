import datetime as dt

import croniter

from base_types import SchoolHoliday
from content import HOLIDAY_DAYS


def get_weekday_str(day: int | dt.date | dt.datetime) -> str:
    if isinstance(day, (dt.date, dt.datetime)):
        day = day.weekday()
    return {
        0: "Montag",
        1: "Dienstag",
        2: "Mittwoch",
        3: "Donnerstag",
        4: "Freitag",
        5: "Samstag",
        6: "Sonntag",
    }[day]


def is_in_holiday(date: dt.date) -> bool:
    return date in HOLIDAY_DAYS


def get_holiday_data_from_date(date: dt.date) -> SchoolHoliday:
    """only call if is_in_holiday(date) returns true, will return none otherwise"""
    return HOLIDAY_DAYS.get(date)  # type: ignore


def get_soonest_weekday() -> dt.date:
    return {
        0: dt.date.today(),
        1: dt.date.today(),
        2: dt.date.today(),
        3: dt.date.today(),
        4: dt.date.today(),
        5: dt.date.today() + dt.timedelta(days=2),
        6: dt.date.today() + dt.timedelta(days=1),
    }[dt.date.today().weekday()]


def get_next_update_time(cron_specs: list[str], start_time: dt.datetime) -> dt.datetime:
    options = []
    for spec in cron_specs:
        cron = croniter.croniter(spec, start_time)
        options.append(cron.get_next(dt.datetime))
    return min(options)
