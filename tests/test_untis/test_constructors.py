import datetime as dt

import pytest

from untis.constructors import announcement_from_dict, ttchange_from_row
from untis.raw_types import RawAnnouncementData, RawTTChange
from untis.types import Announcement, HourInfo, SchoolClass, TimetableChange


@pytest.mark.parametrize(
    ("rowdata", "date", "expected"),
    [
        (
            {"data": ("1 - 12", "Deutsch", "AB (CD)", "Entfall", "Message"), "group": "Q2c"},
            dt.date(2026, 3, 1),
            TimetableChange(
                dt.date(2026, 3, 1),
                SchoolClass(13, "c"),
                HourInfo(1, 12),
                "Deutsch",
                "AB",
                "Message",
                True,
                "CD",
            ),
        ),
    ],
)
def test_ttchange_from_row(rowdata: RawTTChange, date: dt.date, expected: TimetableChange):
    assert ttchange_from_row(rowdata, date) == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            {"subject": "Test Subject", "body": "This is a test body."},
            Announcement("Test Subject", "This is a test body."),
        ),
        (
            {"subject": "", "body": ""},
            Announcement("", ""),
        ),
    ],
)
def test_announcement_from_dict(data: RawAnnouncementData, expected: Announcement):
    assert announcement_from_dict(data) == expected
