import datetime as dt

import pytest

from formatter.utils import find_active_day
from utils import tz


@pytest.mark.parametrize(
    ("dates", "now_time", "expected"),
    [
        (
            [dt.date(2024, 6, 3), dt.date(2024, 6, 4)],
            dt.datetime(2024, 6, 3, 14, 0, tzinfo=tz),
            dt.datetime(2024, 6, 3, tzinfo=tz).date(),
        ),
        (
            [dt.date(2024, 6, 3), dt.date(2024, 6, 4)],
            dt.datetime(2024, 6, 3, 15, 0, tzinfo=tz),
            dt.datetime(2024, 6, 4, tzinfo=tz).date(),
        ),
    ],
)
def test_find_active_day(dates: list[dt.date], now_time: dt.datetime, expected: dt.date):
    """Test find_active_day with various date and time scenarios."""
    assert find_active_day(dates, now_time) == expected
