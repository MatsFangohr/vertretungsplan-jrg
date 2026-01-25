import datetime as dt
from dataclasses import dataclass
from typing import Self, TypedDict


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

    HOUR_DATA = {
        "0 - 11": ("Ganztägig", 0, 0),
        "1 - 6": ("1. bis 3. Block", 1, 6),
        "1 - 9": ("1. bis 4. Block", 1, 9),
        "1 - 11": ("Ganztägig", 0, 0),
        "1 - 2": ("1. Block", 1, 2),
        "3 - 4": ("2. Block", 3, 4),
        "5 - 6": ("3. Block", 5, 6),
        "8 - 9": ("4. Block", 8, 9),
        "10 - 11": ("5. Block", 10, 11),
        "2 - 11": ("Ab 2. Stunde", 2, 11),
        "3 - 11": ("Ab 2. Block", 3, 11),
        "4 - 11": ("Ab 4. Stunde", 4, 11),
        "5 - 11": ("Ab 3. Block", 5, 11),
        "6 - 11": ("Ab 6. Stunde", 6, 11),
        "8 - 11": ("Ab 4. Block", 8, 11),
        "9 - 11": ("Ab 9. Stunde", 9, 11),
    }

    @classmethod
    def from_webuntis_string(cls, data: str) -> Self:
        data = data.strip()

        if data in cls.HOUR_DATA:
            start = cls.HOUR_DATA[data][1]
            end = cls.HOUR_DATA[data][2]
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
        if key in self.HOUR_DATA:
            return self.HOUR_DATA[key][0]
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

        self.message = message

        self.teacher = teacher
        self.originalteacher = originalteacher

        self.lessonname = lessonname

        if not self.teacher and not self.message:
            raise ValueError("needs either teacher or message!")


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
