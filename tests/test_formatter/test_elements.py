import datetime as dt

import pytest

import templates
from formatter.elements import (
    generate_error_message,
    generate_header,
    generate_single_announce_block,
    generate_title,
)
from templates import HTML


@pytest.mark.parametrize(
    ("title", "last_change", "next_update"),
    [
        ("Test Title", dt.datetime(2026, 3, 31, 12, 14), dt.datetime(2026, 10, 2, 0, 0)),
        ("ABCDEFGHIJKLMNOP!", dt.datetime(2024, 1, 1, 16, 32), dt.datetime(2025, 12, 31, 2, 59)),
        (
            "Vertretungsplan für Montag, den 31.02.2024",
            dt.datetime(2025, 6, 7, 8, 9),
            dt.datetime(2024, 2, 29, 6, 37),
        ),
    ],
)
def test_generate_title(title: str, last_change: dt.datetime, next_update: dt.datetime):
    generated = generate_title(title, last_change, next_update)
    dt_format = "%d.%m.%Y, %H:%M"
    assert title in generated
    assert str(last_change.strftime(dt_format)) in generated
    assert str(next_update.strftime(dt_format)) in generated


@pytest.mark.parametrize(
    ("startpage", "last_change", "next_update"),
    [
        (0, dt.datetime(2026, 3, 31, 12, 14), dt.datetime(2026, 10, 2, 0, 0)),
        (1, dt.datetime(2024, 1, 1, 16, 32), dt.datetime(2025, 12, 31, 2, 59)),
        (
            2,
            dt.datetime(2025, 6, 7, 8, 9),
            dt.datetime(2024, 2, 29, 6, 37),
        ),
    ],
)
def test_generate_header(startpage: int, last_change: dt.datetime, next_update: dt.datetime):
    generated = generate_header(startpage, last_change, next_update)
    assert "<title>JRG Vertretungsplan</title>" in generated
    assert "letzteänderungTimestamp" not in generated
    assert "letzteaktTimestamp" not in generated
    assert "nächsteaktTimestamp" not in generated
    assert f"const lastChange = new Date({last_change.timestamp()} * 1000)" in generated
    assert f"const nextUpdate = new Date({next_update.timestamp()} * 1000)" in generated
    assert f"let currentPage = {startpage}" in generated
    assert "function reloadIfRequired()" in generated


@pytest.mark.parametrize(
    ("icon", "subject", "body"),
    [
        ("<svg></svg>", "Test Subject", "Test Body"),
        ("<img src='icon.png'>", "Only Subject", ""),
        ("<div>Icon</div>", "", "Only Body"),
        ("<span>Icon</span>", "", ""),
    ],
)
def test_generate_single_announce_block(icon: HTML, subject: str, body: str):
    generated = generate_single_announce_block(icon, subject, body)
    assert icon in generated
    if subject and body:
        assert f"<h3>{subject}</h3>" in generated
        assert f"<p>{body}</p>" in generated
    elif subject:
        assert "<h3>Ankündigung:</h3>" in generated
        assert f"<p>{subject}</p>" in generated
    elif body:
        assert "<h3>Ankündigung:</h3>" in generated
        assert f"<p>{body}</p>" in generated


def test_generate_error_message():
    generated = generate_error_message()
    assert templates.WARN_ICON in generated
    assert "Fehler bei der Datenverarbeitung!" in generated
    assert templates.ERROR_MESSAGE in generated
