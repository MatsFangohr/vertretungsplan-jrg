import datetime as dt

import croniter

from base_types import SchoolHoliday
from content import HOLIDAY_DAYS

tz = dt.timezone(dt.timedelta(hours=1))

HOUR_DATA = {
    "0 - 11": ("Ganztägig", 0, 0),
    "1 - 6": ("1. bis 3. Block", 1, 6),
    "1 - 9": ("1. bis 4. Block", 1, 9),
    "1 - 11": ("Ganztägig", 0, 0),
    "1 - 2": ("1. Block", 1, 2),
    "3 - 4": ("2. Block", 3, 4),
    "5 - 6": ("3. Block", 5, 6),
    "8 - 9": ("4. Block", 8, 9),
    "10 - 11": ("5. Block", 10, 11),
    "2 - 11": ("Ab 2. Stunde", 2, 11),
    "3 - 11": ("Ab 2. Block", 3, 11),
    "4 - 11": ("Ab 4. Stunde", 4, 11),
    "5 - 11": ("Ab 3. Block", 5, 11),
    "6 - 11": ("Ab 6. Stunde", 6, 11),
    "8 - 11": ("Ab 4. Block", 8, 11),
    "9 - 11": ("Ab 9. Stunde", 9, 11),
}


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
    today = dt.datetime.now(tz).date()
    return {
        0: today,
        1: today,
        2: today,
        3: today,
        4: today,
        5: today + dt.timedelta(days=2),
        6: today + dt.timedelta(days=1),
    }[today.weekday()]


def get_next_update_time(cron_specs: list[str], start_time: dt.datetime) -> dt.datetime:
    options = []
    for spec in cron_specs:
        cron = croniter.croniter(spec, start_time)
        options.append(cron.get_next(dt.datetime))
    return min(options)
