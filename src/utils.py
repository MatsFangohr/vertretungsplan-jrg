import datetime as dt
import re
import zoneinfo

import croniter

from formatter.types import HTML
from untis.data import HOLIDAY_DAYS
from untis.types import SchoolHoliday

tz = zoneinfo.ZoneInfo("Europe/Berlin")


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
    return get_soonest_weekday_to(today)


def get_soonest_weekday_to(date: dt.date) -> dt.date:
    return {
        0: date,
        1: date,
        2: date,
        3: date,
        4: date,
        5: date + dt.timedelta(days=2),
        6: date + dt.timedelta(days=1),
    }[date.weekday()]


def get_next_update_time(cron_specs: list[str], start_time: dt.datetime) -> dt.datetime:
    options = []
    for spec in cron_specs:
        cron = croniter.croniter(spec, start_time)
        options.append(cron.get_next(dt.datetime))
    return min(options)


def strip_html(data: HTML) -> str:
    return re.sub("<[^>]+>", "", data)
