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
from formatting import parse_lesson_name, parse_message
from utils import (
    HOUR_DATA,
    strip_html,
    tz,
)


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
