import datetime as dt
from dataclasses import dataclass
from typing import ClassVar, Self


@dataclass
class SchoolHoliday:
    name: str
    start: dt.date  # first date at which the message should be shown
    end: dt.date  # final date at which the message should be shown
    first_day_after: dt.date  # first day of school after the holidays


@dataclass(frozen=True)
class SchoolClass:
    year: int
    letter: str

    letters_to_year: ClassVar[dict[str, int]] = {"Q2": 13, "Q1": 12, "Ej": 11, "DAZ": 1, "Verw": 99}
    year_to_letters: ClassVar[dict[int, str]] = {
        year: letter for letter, year in letters_to_year.items()
    }

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


@dataclass
class Announcement:
    subject: str
    body: str


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


@dataclass
class WebUntisData:
    date: dt.date
    changes: list[TimetableChange]
    announcements: list[Announcement]
    weekday: str
    last_update: dt.datetime
    created_with_error: bool
