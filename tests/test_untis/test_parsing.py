import datetime as dt

import pytest

from untis.parsing import (
    LESSON_NAMES,
    _parse_message_substitutions,
    _parse_message_verlegungen,
    hour_to_name,
    is_start_of_block,
    parse_lesson_name,
    strip_html,
    time_to_hour,
)


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        ("<span>test</span>", "test"),
        ('<a href="https://example.com">link</a>', "link"),
    ],
)
def test_strip_html(html: str, expected: str):
    assert strip_html(html) == expected


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
    ("msg", "expected"),
    [
        ("AA @ home", "Aufgaben (zuhause)"),
        ("Desy ", "DESY"),
        ("letzte Stunde f.a.", "letzte Stunde fällt aus"),
        ("3. Block LaaO", "3. Block Lernen am anderen Ort"),
        ("AA zuhause", "Aufgaben zuhause"),
    ],
)
def test_parse_message_substitutions(msg: str, expected: str):
    assert _parse_message_substitutions(msg) == expected


@pytest.mark.parametrize(
    ("msg", "date", "expected"),
    [
        ("Verlegung von 23.2. / 7:50", dt.date(2026, 2, 23), "Verlegung aus dem 1. Block"),
        (
            "Verlegung von 23.2. / 7:50",
            dt.date(2026, 2, 19),
            "Verlegung aus dem 1. Block vom Montag, 23.02.2026",
        ),
        ("Verlegung von 21.5. / 14:20", dt.date(2026, 5, 21), "Verlegung aus dem 4. Block"),
        (
            "Verlegung von 21.5. / 14:20",
            dt.date(2026, 5, 20),
            "Verlegung aus dem 4. Block vom Donnerstag, 21.05.2026",
        ),
        ("Verlegung nach 9.6. / 12:35", dt.date(2026, 6, 9), "Verlegt in die 6. Stunde"),
        (
            "Verlegung nach 9.6. / 12:35",
            dt.date(2026, 6, 8),
            "Verlegt auf Dienstag, 09.06.2026 in der 6. Stunde",
        ),
    ],
)
def test_parse_message_verlegungen(msg: str, date: dt.date, expected: str):
    assert _parse_message_verlegungen(msg, date) == expected


@pytest.mark.parametrize(("name", "expected"), [*list(LESSON_NAMES.items()), ("Test", "Test")])
def test_parse_lesson_name(name: str, expected: str):
    assert parse_lesson_name(name) == expected
