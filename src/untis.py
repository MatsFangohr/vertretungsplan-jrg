from __future__ import annotations

import asyncio
import datetime as dt
import re
from dataclasses import dataclass
from typing import Self

import aiohttp

from base_types import (
    HTML,
    RawAnnouncementData,
    RawTTChange,
    RawWebUntisData,
    SchoolClass,
)
from content import SetupData
from logger import warn
from utils import HOUR_DATA, get_weekday_str, hour_to_name, is_start_of_block, time_to_hour, tz


class WebUntisManager:
    url: str

    def __init__(self) -> None:
        self.url = (
            "https://rist2024.webuntis.com/WebUntis/monitor/substitution/data?school=rist2024"
        )

    async def get_data(self, session: aiohttp.ClientSession, date: dt.date) -> RawWebUntisData:
        payload = {"date": int(date.strftime("%Y%m%d"))} | SetupData.BASE_PAYLOAD
        async with session.post(self.url, json=payload) as r:
            return (await r.json())["payload"]

    async def get_multiple(self, dates: list[dt.date]) -> dict[dt.date, RawWebUntisData]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_data(session, d) for d in dates]
            results = await asyncio.gather(*tasks)
        return dict(zip(dates, results, strict=True))


@dataclass
class HourInfo:
    start: int
    end: int
    needs_suffix: bool

    @classmethod
    def from_webuntis_string(cls, data: str) -> Self:
        data = data.strip()

        if data in HOUR_DATA:
            needs_suffix = False
            start = HOUR_DATA[data][1]
            end = HOUR_DATA[data][2]
        else:
            needs_suffix = True
            match list(data.split(" ")):
                case [single_number]:
                    start = end = int(single_number)
                case [st, "-", ed]:
                    start = int(st)
                    end = int(ed)
                    if start >= end:
                        raise ValueError(f"hour '{data}' ends before it starts!")
                case _:
                    start = end = 0
                    warn(f"unrecognized time format: '{data}'!")

        return cls(start, end, needs_suffix)

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


class TimetableChange:
    hours: HourInfo
    lessonname: str
    teacher: str
    message: str
    klasse: SchoolClass
    canceled: bool
    originalteacher: str

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

        self.parse_message()

        self.teacher = TimetableChange.strip_html(teacher.upper().strip())
        self.originalteacher = TimetableChange.strip_html(originalteacher.upper().strip())

        self.lessonname = TimetableChange.parse_lesson_name(lessonname)

        if not self.hours:
            raise ValueError("no hours!")
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
                        (TimetableChange.strip_html(teacherinfo).replace("-", "").replace(",", "")),
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

        # marker for ausfall
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

    # quite crude but does the job
    @staticmethod
    def strip_html(data: str) -> str:
        return re.sub("<[^>]+>", "", data)

    def repr_stripped(self) -> str:
        return TimetableChange.strip_html(self.repr_html())

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
                            out += f"{hours}: {self.lessonname} bei {self.teacher.replace('--- , ', '')} findet <span style='color: {SetupData.get_color(self.klasse.year, 'dark')}'>ohne {self.originalteacher}</span> statt"  # noqa: E501
                        else:
                            out += f"{hours}: {self.lessonname} bei {self.teacher} <span style='color: {SetupData.get_color(self.klasse.year, 'dark')}'>statt {self.originalteacher}</span>"  # noqa: E501
                    else:
                        out += f"{hours}: {self.lessonname} bei {self.teacher}"
                else:  # noqa: PLR5501
                    if self.originalteacher:
                        out += f"{hours} bei {self.teacher} <span style='color: {SetupData.get_color(self.klasse.year, 'dark')}'>statt {self.originalteacher}</span>"  # noqa: E501
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

    def parse_message(self) -> None:
        """basic replacements to improve message legibility'"""
        stripped_message = self.message.replace(" ", "").strip()
        COMPLETE_REPLACEMENTS = {  # noqa: N806
            "AA": "Aufgaben",
            "AA@home": "Aufgaben (zuhause)",
            "Desy": "DESY",
        }

        if stripped_message in COMPLETE_REPLACEMENTS:
            self.message = COMPLETE_REPLACEMENTS[stripped_message]

        PARTIAL_REPLACEMENTS = {  # noqa: N806
            "f.a.": "fällt aus",
            "LaaO": "Lernen am anderen Ort",
        }

        for keyword, replacement in PARTIAL_REPLACEMENTS.items():
            self.message = self.message.replace(keyword, replacement)

        if mat := re.search(r"Verlegung (nach|von) (\d?\d\.\d?\d\.) \/ (\d?\d:\d\d)", self.message):
            date = (
                dt.datetime.strptime(mat.group(2), "%d.%m.")  # noqa: DTZ007 see two lines below
                .replace(year=dt.datetime.now(tz).year)
                .astimezone(tz)
                .date()
            )
            if date.month == 1 and dt.datetime.now(tz).month == 12:
                date = date.replace(year=date.year + 1)

            time = dt.datetime.strptime(mat.group(3), "%H:%M").time().replace(tzinfo=tz)  # noqa: DTZ007

            improved = ""

            if mat.group(1) == "nach":
                if self.date == date:
                    improved += "Verlegt in "
                    if hour := time_to_hour(time):
                        if is_start_of_block(hour):
                            improved += f"den {hour_to_name(hour)}"
                        else:
                            improved += f"die {hour_to_name(hour)}"
                    else:
                        improved += f"verlegt nach {time.strftime('%H:%M')}"
                else:
                    improved += f"Verlegt auf {get_weekday_str(date)}, {date.strftime('%d.%m.%Y')} "
                    if hour := time_to_hour(time):
                        if is_start_of_block(hour):
                            improved += f"im {hour_to_name(hour)}"
                        else:
                            improved += f"in der {hour_to_name(hour)}"
                    else:
                        improved += time.strftime("%H:%M")
            elif mat.group(1) == "von":
                if self.date == date:
                    improved += "Verlegung "
                    if hour := time_to_hour(time):
                        if is_start_of_block(hour):
                            improved += f"aus dem {hour_to_name(hour)}"
                        else:
                            improved += f"aus der {hour_to_name(hour)}"
                    else:
                        improved += f"von {time.strftime('%H:%M')}"
                else:
                    improved += "Verlegung "
                    if hour := time_to_hour(time):
                        if is_start_of_block(hour):
                            improved += f"aus dem {hour_to_name(hour)} "
                        else:
                            improved += f"aus der {hour_to_name(hour)} "
                    else:
                        improved += f"von {time.strftime('%H:%M')} "
                    improved += f"vom {get_weekday_str(date)}, {date.strftime('%d.%m.%Y')}"

            self.message = self.message.replace(mat.group(0), improved)

    @staticmethod
    def parse_lesson_name(name: str) -> str:
        """expands lesson names and returns the short version if not found"""
        stripname = name.strip()
        if stripname in SetupData.LESSON_NAMES:
            return SetupData.LESSON_NAMES[stripname]
        else:
            warn(f"can't find lesson name: {name}")
            return stripname

    @staticmethod
    def parse_klasse(klasse: str) -> tuple[int, str]:
        """grabs year number and class letter from class name where possible"""
        year = 0
        match list(klasse.strip()):
            case ["Q", "2", _]:
                year = 13
            case ["Q", "1", _]:
                year = 12
            case ["E", "j", _]:
                year = 11
            case ["1", "0", _]:
                year = 10
            case [yr, letter]:
                return (int(yr), letter)
            case ["D", "A", "Z"]:
                return (1, "a")
            case ["V", "e", "r", "w"]:
                return (99, "a")
            case _:
                raise ValueError(f"invalid klasse: '{klasse}'!")
        return (year, klasse[-1])


class Announcement:
    subject: str
    body: str

    def __init__(self, subject: str, body: str) -> None:
        self.subject = subject
        self.body = body

    @classmethod
    def from_dict(cls, data: RawAnnouncementData) -> Self:
        return cls(data["subject"], data["body"])


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
