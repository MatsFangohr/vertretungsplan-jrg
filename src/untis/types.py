from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from typing import Self, TypedDict

import formatter
from formatter.types import (
    HTML,
)
from untis.data import HOUR_DATA
from untis.parsing import parse_lesson_name, parse_message
from utils import strip_html, tz


class RawAnnouncementData(TypedDict):
    subject: str
    body: str


class RawAnnouncementsData(TypedDict):
    messages: list[RawAnnouncementData]


class RawTTChange(TypedDict):
    data: tuple[str, str, str, str, str]
    group: str


class RawWebUntisData(TypedDict):
    date: str
    rows: list[RawTTChange]
    messageData: RawAnnouncementsData
    weekDay: str
    lastUpdate: str


class SchoolHoliday(TypedDict):
    name: str
    start: dt.date  # first date at which the message should be shown
    end: dt.date  # final date at which the message should be shown
    first_day_after: dt.date  # first day of school after the holidays


class SchoolClass:
    year: int
    letter: str

    letters_to_year = {"Q2": 13, "Q1": 12, "Ej": 11, "DAZ": 1, "Verw": 99}
    year_to_letters: dict[int, str] = {year: letter for letter, year in letters_to_year.items()}

    def __init__(self, year: int, letter: str) -> None:
        self.year = year
        self.letter = letter

    @classmethod
    def from_string(cls, data: str) -> Self:
        match list(data.strip()):
            case ["Q", "2", _]:
                year = SchoolClass.letters_to_year["Q2"]
            case ["Q", "1", _]:
                year = SchoolClass.letters_to_year["Q1"]
            case ["E", "j", _]:
                year = SchoolClass.letters_to_year["Ej"]
            case ["1", "0", _]:
                year = 10
            case [yr, letter]:
                return cls(int(yr), letter)
            case ["D", "A", "Z"]:
                return cls(SchoolClass.letters_to_year["DAZ"], "")
            case ["V", "e", "r", "w"]:
                return cls(SchoolClass.letters_to_year["Verw"], "")
            case _:
                raise ValueError(f"invalid klasse: '{data}'!")
        return cls(year, data[-1])

    def to_string(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        if self.year in SchoolClass.year_to_letters:
            return SchoolClass.year_to_letters[self.year] + self.letter
        return str(self.year) + self.letter

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SchoolClass):
            return self.year == other.year and self.letter == other.letter
        return False

    def __hash__(self) -> int:
        return hash(self.letter) ^ hash(str(self.year))


@dataclass
class HourInfo:
    start: int
    end: int

    @classmethod
    def from_webuntis_string(cls, data: str) -> Self:
        data = data.strip()

        if data in HOUR_DATA:
            start = HOUR_DATA[data][1]
            end = HOUR_DATA[data][2]
        else:
            match list(data.split(" ")):
                case [single_number]:
                    start = end = int(single_number)
                case [st, "-", ed]:
                    start = int(st)
                    end = int(ed)
                    if start >= end:
                        raise ValueError(f"hour '{data}' ends before it starts!")
                case _:
                    raise ValueError(f"unrecognized time format: '{data}'!")

        return cls(start, end)

    def to_string(self) -> str:
        key = f"{self.start} - {self.end}"
        if key in HOUR_DATA:
            return HOUR_DATA[key][0]
        elif self.start == self.end:
            return f"{self.start}. Stunde"
        else:
            return f"{key}. Stunde"

    def to_sorttuple(self) -> tuple[int, int]:
        return (self.start, self.end)


class Announcement:
    subject: str
    body: str

    def __init__(self, subject: str, body: str) -> None:
        self.subject = subject
        self.body = body

    @classmethod
    def from_dict(cls, data: RawAnnouncementData) -> Self:
        return cls(data["subject"], data["body"])


@dataclass
class TimetableChange:
    date: dt.date
    klasse: SchoolClass  # affected class
    hours: HourInfo  # when does the change take place
    lessonname: str
    teacher: str  # substitute teacher
    message: str
    canceled: bool
    originalteacher: str  # ill / absent teacher

    def __init__(
        self,
        date: dt.date,
        hours: HourInfo,
        klasse: SchoolClass,
        lessonname: str,
        teacher: str,
        originalteacher: str,
        message: str,
        canceled: bool,
    ) -> None:
        self.date = date
        self.hours = hours
        self.klasse = klasse
        self.message = message
        self.canceled = canceled

        self.message = parse_message(message, date)

        self.teacher = strip_html(teacher.upper().strip())
        self.originalteacher = strip_html(originalteacher.upper().strip())

        self.lessonname = parse_lesson_name(lessonname)

        if not self.teacher and not self.message:
            raise ValueError("needs either teacher or message!")

    @classmethod
    def from_row(cls, rowdata: RawTTChange, date: dt.date) -> TimetableChange:
        klasse = SchoolClass.from_string(rowdata["group"])

        hours_str, lessonname, teacherinfo, status, message = rowdata["data"]

        hours = HourInfo.from_webuntis_string(hours_str)

        if klasse == "Verw":
            newteacher = ", ".join(
                filter(
                    lambda teacher: teacher != "",
                    re.sub(
                        "\\([^)]+\\)",
                        "",
                        (strip_html(teacherinfo).replace("-", "").replace(",", "")),
                    ).split(" "),
                )
            )
            originalteacher = ""
        else:
            newteacher = re.sub("\\(.*\\)", "", teacherinfo)
            originalteacher = re.sub(
                "^[^\\(]*\\(|\\)[^\\(]*$",
                "",
                re.sub("\\).*?\\(", ", ", teacherinfo) if "(" in teacherinfo else "",
            )

        if status.strip() == "Entfall":
            entfall = True
        else:
            entfall = False
            # if status isn't "Entfall" then add it to the end of the message string
            if status.strip() and message.strip():
                message += f" / {status}"
            elif status.strip() and not message.strip():
                message = status

        return cls(date, hours, klasse, lessonname, newteacher, originalteacher, message, entfall)

    def __repr__(self) -> str:
        base = "[c] " if self.canceled else ""
        return base + f"{self.klasse} | {self.repr_stripped()}"

    def repr_stripped(self) -> str:
        return strip_html(self.repr_html())

    # TODO: move into formatting and away from logic
    def repr_html(self) -> HTML:
        out = ""
        hours = self.hours.to_string()
        if self.canceled:
            if self.teacher:
                if self.lessonname:
                    out += f"{hours}: {self.lessonname} bei {self.teacher}"
                else:
                    out += f"{hours} bei {self.teacher}"
            else:  # noqa: PLR5501
                if self.lessonname:
                    out += f"{hours} ({self.lessonname})"
                else:
                    out += f"{hours}"
            out += " <b>fällt aus</b>"
            if self.message:
                out += f": {self.message}"
        else:
            if self.teacher:
                if self.lessonname:
                    if self.originalteacher:
                        if "---" in self.teacher:
                            out += f"{hours}: {self.lessonname} bei {self.teacher.replace('--- , ', '')} findet <span style='color: {formatter.get_color(self.klasse.year, 'dark')}'>ohne {self.originalteacher}</span> statt"  # noqa: E501
                        else:
                            out += f"{hours}: {self.lessonname} bei {self.teacher} <span style='color: {formatter.get_color(self.klasse.year, 'dark')}'>statt {self.originalteacher}</span>"  # noqa: E501
                    else:
                        out += f"{hours}: {self.lessonname} bei {self.teacher}"
                else:  # noqa: PLR5501
                    if self.originalteacher:
                        out += f"{hours} bei {self.teacher} <span style='color: {formatter.get_color(self.klasse.year, 'dark')}'>statt {self.originalteacher}</span>"  # noqa: E501
                    else:
                        out += f"{hours} bei {self.teacher}"
            else:  # noqa: PLR5501
                if self.lessonname:
                    out += f"{hours} ({self.lessonname})"
                else:
                    out += f"{hours}"
            if self.message:
                out += f": {self.message}"
        return out


@dataclass
class WebUntisData:
    date: dt.date
    changes: list[TimetableChange]
    announcements: list[Announcement]
    weekday: str
    last_update: dt.datetime
    created_with_error: bool

    def __init__(
        self,
        date: dt.date,
        changes: list[TimetableChange],
        announcements: list[Announcement],
        weekday: str,
        last_update: dt.datetime,
        created_with_error: bool,
    ) -> None:
        self.date = date
        self.changes = changes
        self.announcements = announcements
        self.weekday = weekday
        self.last_update = last_update
        self.created_with_error = created_with_error

    @classmethod
    def from_raw_data(cls, data: RawWebUntisData) -> Self:
        date = dt.datetime.strptime(str(data["date"]), "%Y%m%d").astimezone(tz).date()
        ttchanges = [TimetableChange.from_row(row, date) for row in data["rows"]]
        announcements = list(map(Announcement.from_dict, data["messageData"]["messages"]))

        return cls(
            date=date,
            changes=ttchanges,
            announcements=announcements,
            weekday=data["weekDay"],
            last_update=dt.datetime.strptime(data["lastUpdate"], "%d.%m.%Y %H:%M:%S").astimezone(
                tz
            ),
            created_with_error=False,
        )
