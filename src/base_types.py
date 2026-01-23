from __future__ import annotations

import datetime as dt
from typing import Self, TypedDict

type HTML = str


class HTMLFiles(TypedDict):
    main: HTML
    about: HTML


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


class ColorDict(TypedDict):
    pale: str
    dark: str
    normal: str
    strong: str


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
