import datetime as dt
import zoneinfo

import croniter

tz = zoneinfo.ZoneInfo("Europe/Berlin")


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


def get_soonest_weekday() -> dt.date:
    return get_soonest_weekday_to(today())


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
    """Parses given cron specifications and (assuming they are all active) returns the next time one
    will be called.
    """
    if not cron_specs:
        return now()
    options = []
    for spec in cron_specs:
        cron = croniter.croniter(spec, start_time)
        options.append(cron.get_next(dt.datetime))
    return min(options)


def now() -> dt.datetime:
    """Returns a timezone-aware datetime.now() object in the Europe/Berlin timezone."""
    return dt.datetime.now(tz)


def today() -> dt.date:
    """Returns a timezone-aware date.today() object in the Europe/Berlin timezone."""
    return now().date()
