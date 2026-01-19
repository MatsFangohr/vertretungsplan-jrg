import datetime as dt
import zoneinfo

import croniter

from base_types import SchoolHoliday
from content import HOLIDAY_DAYS

tz = zoneinfo.ZoneInfo("Europe/Berlin")

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


def hour_to_name(hour: int) -> str:
    LUT = {
        1: "1. Block",
        3: "2. Block",
        5: "3. Block",
        8: "4. Block",
        10: "5. Block",
        2: "2. Stunde",
        4: "4. Stunde",
        6: "6. Stunde",
        7: "Mittagspause",
        9: "9. Stunde",
        11: "11. Stunde",
        12: "12. Stunde",
    }

    if hour in LUT:
        return LUT[hour]
    else:
        return f"{hour}. Stunde"


def is_start_of_block(hour: int) -> bool:
    return hour in [1, 3, 5, 8, 10]


def time_to_hour(time: dt.time) -> int | None:
    LUT = {
        "07:50": 1,
        "08:35": 2,
        "09:50": 3,
        "10:35": 4,
        "11:50": 5,
        "12:35": 6,
        "13:20": 7,
        "13:35": 7,
        "14:20": 8,
        "15:05": 9,
        "15:50": 10,
        "16:05": 11,
        "16:50": 12,
    }

    time_str = time.strftime("%H:%M")
    return LUT.get(time_str)


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
