import datetime as dt
import zoneinfo

import pytest

from utils import (
    get_soonest_weekday_to,
    get_weekday_str,
    hour_to_name,
    is_start_of_block,
    strip_html,
    time_to_hour,
    tz,
)


def test_tz():
    assert tz == zoneinfo.ZoneInfo("Europe/Berlin")


@pytest.mark.parametrize(
    ("hour", "expected"),
    [
        (1, "1. Block"),
        (3, "2. Block"),
        (5, "3. Block"),
        (8, "4. Block"),
        (10, "5. Block"),
        (2, "2. Stunde"),
        (4, "4. Stunde"),
        (6, "6. Stunde"),
        (7, "Mittagspause"),
        (9, "9. Stunde"),
        (11, "11. Stunde"),
        (12, "12. Stunde"),
        (13, "13. Stunde"),
        (0, "0. Stunde"),
        (1254364, "1254364. Stunde"),
    ],
)
def test_hour_to_name(hour: int, expected: str):
    assert hour_to_name(hour) == expected


@pytest.mark.parametrize(
    ("hour", "expected"),
    [
        (1, True),
        (2, False),
        (3, True),
        (4, False),
        (5, True),
        (6, False),
        (7, False),
        (8, True),
        (9, False),
        (10, True),
        (11, False),
    ],
)
def test_is_start_of_block(hour: int, expected: bool):
    assert is_start_of_block(hour) == expected


@pytest.mark.parametrize(
    ("time", "expected"),
    [
        (dt.time(7, 50), 1),
        (dt.time(8, 35), 2),
        (dt.time(9, 50), 3),
        (dt.time(10, 35), 4),
        (dt.time(11, 50), 5),
        (dt.time(12, 35), 6),
        (dt.time(13, 20), 7),
        (dt.time(13, 35), 7),
        (dt.time(14, 20), 8),
        (dt.time(15, 5), 9),
        (dt.time(15, 50), 10),
        (dt.time(16, 5), 11),
        (dt.time(16, 50), 12),
        (dt.time(7, 49), None),
        (dt.time(17, 50), None),
        (dt.time(19, 50), None),
    ],
)
def test_time_to_hour(time: dt.time, expected: int | None):
    assert time_to_hour(time) == expected


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


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        ("<span>test</span>", "test"),
        ('<a href="https://example.com">link</a>', "link"),
    ],
)
def test_strip_html(html: str, expected: str):
    assert strip_html(html) == expected
