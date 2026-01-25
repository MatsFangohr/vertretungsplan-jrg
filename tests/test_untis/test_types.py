import datetime as dt

import pytest

from untis import ttchange_from_row
from untis.raw_types import RawTTChange
from untis.types import HourInfo, SchoolClass, TimetableChange


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ("1 - 2", HourInfo(1, 2)),
        ("3 - 4", HourInfo(3, 4)),
        ("7 - 14", HourInfo(7, 14)),
        ("1534 - 6456", HourInfo(1534, 6456)),
        ("0 - 3", HourInfo(0, 3)),
    ],
)
def test_hourinfo_from_string(data: str, expected: HourInfo):
    assert HourInfo.from_webuntis_string(data) == expected


@pytest.mark.parametrize(
    ("data"),
    [
        ("3 - 0"),
        ("2 - 1"),
        ("14 - 7"),
    ],
)
def test_hourinfo_from_string_backwards_time(data: str):
    with pytest.raises(ValueError, match="ends before it starts"):
        HourInfo.from_webuntis_string(data)


@pytest.mark.parametrize(
    ("data"),
    [
        ("3 -6 -5"),
        ("25 36"),
        ("45- 4"),
    ],
)
def test_hourinfo_from_string_invalid_data(data: str):
    with pytest.raises(ValueError, match="unrecognized time format"):
        HourInfo.from_webuntis_string(data)


@pytest.mark.parametrize(
    ("info", "expected"),
    [
        (HourInfo(1, 2), "1. Block"),
        (HourInfo(3, 4), "2. Block"),
        (HourInfo(8, 9), "4. Block"),
        (HourInfo(0, 11), "Ganztägig"),
        (HourInfo(2, 11), "Ab 2. Stunde"),
        (HourInfo(2, 9), "2 - 9. Stunde"),
        (HourInfo(0, 1), "0 - 1. Stunde"),
    ],
)
def test_hourinfo_to_string(info: HourInfo, expected: str):
    assert info.to_string() == expected


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (1, 2),
        (3, 4),
        (0, 14),
        (67, 234),
    ],
)
def test_hourinfo_to_sorttuple(start: int, end: int):
    assert HourInfo(start, end).to_sorttuple() == (start, end)


def test_ttchange_init_errors():
    with pytest.raises(ValueError, match="needs either teacher or message"):
        TimetableChange(
            dt.date(2026, 1, 1), HourInfo(1, 2), SchoolClass(5, "a"), "Mathe", "", "", "", False
        )


@pytest.mark.parametrize(
    ("rowdata", "date", "expected"),
    [
        (
            {"data": ("1 - 12", "Deutsch", "AB (CD)", "Entfall", "Message"), "group": "Q2c"},
            dt.date(2026, 3, 1),
            TimetableChange(
                dt.date(2026, 3, 1),
                HourInfo(1, 12),
                SchoolClass(13, "c"),
                "Deutsch",
                "AB",
                "CD",
                "Message",
                True,
            ),
        ),
    ],
)
def test_ttchange_from_row(rowdata: RawTTChange, date: dt.date, expected: TimetableChange):
    assert ttchange_from_row(rowdata, date) == expected
