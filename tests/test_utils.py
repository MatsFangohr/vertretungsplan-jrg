import datetime as dt
import zoneinfo

import pytest

from utils import (
    get_next_update_time,
    get_soonest_weekday_to,
    get_weekday_str,
    tz,
)


def test_tz():
    assert tz == zoneinfo.ZoneInfo("Europe/Berlin")


@pytest.mark.parametrize(
    ("date", "expected"),
    [
        (dt.date(2026, 1, 1), dt.date(2026, 1, 1)),
        (dt.date(2026, 1, 2), dt.date(2026, 1, 2)),
        (dt.date(2026, 1, 3), dt.date(2026, 1, 5)),
        (dt.date(2026, 1, 4), dt.date(2026, 1, 5)),
        (dt.date(2026, 1, 5), dt.date(2026, 1, 5)),
        (dt.date(2026, 1, 6), dt.date(2026, 1, 6)),
        (dt.date(2026, 1, 7), dt.date(2026, 1, 7)),
        (dt.date(2027, 1, 1), dt.date(2027, 1, 1)),
        (dt.date(2027, 1, 2), dt.date(2027, 1, 4)),
        (dt.date(2027, 1, 3), dt.date(2027, 1, 4)),
    ],
)
def test_get_soonest_weekday_to(date: dt.date, expected: dt.date):
    assert get_soonest_weekday_to(date) == expected


start_of_year = dt.datetime(2026, 1, 1, 0, 0, tzinfo=tz)


@pytest.mark.parametrize(
    ("cron_specs", "start_time", "expected"),
    [
        ([], start_of_year, start_of_year),
        ([], start_of_year + dt.timedelta(minutes=1), start_of_year + dt.timedelta(minutes=1)),
        (
            ["* * * * *"],
            start_of_year,
            dt.datetime(2026, 1, 1, 0, 1, tzinfo=tz),
        ),
        (["0 * * * *"], start_of_year, dt.datetime(2026, 1, 1, 1, 0, tzinfo=tz)),
        (["0 0 * * *"], start_of_year, dt.datetime(2026, 1, 2, 0, 0, tzinfo=tz)),
        (["0 0 * * 0"], start_of_year, dt.datetime(2026, 1, 4, 0, 0, tzinfo=tz)),
        (["0 0 * * 5"], start_of_year, dt.datetime(2026, 1, 2, 0, 0, tzinfo=tz)),
        (["0 0 * * 6"], start_of_year, dt.datetime(2026, 1, 3, 0, 0, tzinfo=tz)),
        (["0 */2 * * *"], start_of_year, dt.datetime(2026, 1, 1, 2, 0, tzinfo=tz)),
        (
            ["0 */2 * * *"],
            dt.datetime(2026, 1, 1, 23, 0, tzinfo=tz),
            dt.datetime(2026, 1, 2, 0, 0, tzinfo=tz),
        ),
    ],
)
def test_get_next_update_time_empty(
    cron_specs: list[str], start_time: dt.datetime, expected: dt.datetime
):
    assert get_next_update_time(cron_specs, start_time) == expected


@pytest.mark.parametrize(
    ("day", "expected"),
    [
        (0, "Montag"),
        (1, "Dienstag"),
        (2, "Mittwoch"),
        (3, "Donnerstag"),
        (4, "Freitag"),
        (5, "Samstag"),
        (6, "Sonntag"),
        (dt.date(2026, 3, 2), "Montag"),
        (dt.date(2026, 3, 3), "Dienstag"),
        (dt.date(2026, 3, 4), "Mittwoch"),
        (dt.date(2026, 3, 5), "Donnerstag"),
        (dt.date(2026, 3, 6), "Freitag"),
        (dt.date(2026, 3, 7), "Samstag"),
        (dt.date(2026, 3, 8), "Sonntag"),
        (dt.datetime(2026, 3, 9, 00, 00), "Montag"),
        (dt.datetime(2026, 3, 10, 23, 59), "Dienstag"),
        (dt.datetime(2026, 3, 11, 12, 00), "Mittwoch"),
        (dt.datetime(2026, 3, 12, 7, 50), "Donnerstag"),
        (dt.datetime(2026, 3, 13, 13, 20), "Freitag"),
        (dt.datetime(2026, 3, 14, 14, 20), "Samstag"),
        (dt.datetime(2026, 3, 15, 15, 50), "Sonntag"),
    ],
)
def test_get_weekday_str(day: int | dt.date | dt.datetime, expected: str):
    assert get_weekday_str(day) == expected
