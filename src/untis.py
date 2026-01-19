from __future__ import annotations

import asyncio
import datetime as dt
import re
from typing import Self

import aiohttp

import utils
from base_types import (
    HTML,
    RawAnnouncementData,
    RawTTChange,
    RawWebUntisData,
    SchoolClass,
)
from content import SetupData
from logger import warn
from utils import tz


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


class HourInfo:
    data: str
    start: int
    end: int
    needs_suffix: bool

    def __init__(self, data: str, needs_suffix: bool = True) -> None:
        self.needs_suffix = needs_suffix

        self.data = data.strip()
        try:
            match list(self.data.split(" ")):
                case [start, "-", end]:
                    self.start = int(start)
                    self.end = int(end)
                    if self.start >= self.end:
                        raise ValueError("hour ends before it starts!")
                case [single_digit]:
                    self.start = self.end = int(single_digit)
                case _:
                    self.start = self.end = 0
                    warn(f"unrecognized time format: '{data}'!")
        except ValueError:
            warn(f"invalid time format: '{data}'!")

    @classmethod
    def from_data(cls, data: str, needs_suffix: bool, start: int, end: int) -> HourInfo:
        hourinfo = HourInfo("1", needs_suffix)
        hourinfo.data = data
        hourinfo.start = start
        hourinfo.end = end

        return hourinfo

    def parse_data(self) -> HourInfo:
        if self.data in utils.HOUR_DATA:
            return HourInfo.from_data(
                utils.HOUR_DATA[self.data][0],
                False,
                utils.HOUR_DATA[self.data][1],
                utils.HOUR_DATA[self.data][2],
            )

        return self

    def to_string(self) -> str:
        if self.needs_suffix:
            return self.data + ". Stunde"
        else:
            return self.data

    def to_sorttuple(self) -> tuple[int, int]:
        return (self.start, self.end)

    def __repr__(self) -> str:
        return f"{self.start}-{self.end}"


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
        hours: HourInfo,
        klasse: SchoolClass,
        lessonname: str,
        teacher: str,
        originalteacher: str,
        message: str,
        canceled: bool,
    ) -> None:
        self.canceled = canceled

        self.hours = hours
        self.klasse = klasse

        self.teacher = TimetableChange.strip_html(teacher.upper().strip())
        self.originalteacher = TimetableChange.strip_html(originalteacher.upper().strip())

        self.message = TimetableChange.parse_message(message)
        self.lessonname = TimetableChange.parse_lesson_name(lessonname)

        if not self.hours:
            raise ValueError("no hours!")
        if not self.teacher and not self.message:
            raise ValueError("needs either teacher or message!")

    @classmethod
    def from_row(cls, rowdata: RawTTChange) -> TimetableChange:
        klasse = SchoolClass.from_string(rowdata["group"])

        hours_str, lessonname, teacherinfo, status, message = rowdata["data"]

        hours = HourInfo(hours_str).parse_data()

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

        return cls(hours, klasse, lessonname, newteacher, originalteacher, message, entfall)

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

    @staticmethod
    def parse_message(message: str) -> str:
        """basic replacements to improve message legibility'"""
        stripped_message = message.replace(" ", "").strip()
        if stripped_message == "AA":
            return "Aufgaben"
        elif stripped_message == "AA@home":
            return "Aufgaben (zuhause)"
        elif stripped_message == "Desy":
            return "DESY"
        else:
            replacements = {
                "f.a.": "fällt aus",
                "LaaO": "Lernen am anderen Ort",
            }
            for keyword, replacement in replacements.items():
                message = message.replace(keyword, replacement)
            return message

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
    def from_raw_data(cls, data: RawWebUntisData) -> WebUntisData:
        ttchanges = list(map(TimetableChange.from_row, data["rows"]))
        announcements = list(map(Announcement.from_dict, data["messageData"]["messages"]))

        return WebUntisData(
            date=dt.datetime.strptime(str(data["date"]), "%Y%m%d").astimezone(tz).date(),
            changes=ttchanges,
            announcements=announcements,
            weekday=data["weekDay"],
            last_update=dt.datetime.strptime(data["lastUpdate"], "%d.%m.%Y %H:%M:%S").astimezone(
                tz
            ),
            created_with_error=False,
        )
