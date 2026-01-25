import datetime as dt
import zoneinfo

import pytest

from utils import (
    get_soonest_weekday_to,
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
