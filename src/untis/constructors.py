from __future__ import annotations

import datetime as dt
import re

import utils
from logger import warn
from untis.parsing import parse_lesson_name, parse_message, strip_html
from untis.raw_types import RawAnnouncementData, RawTTChange, RawWebUntisData
from untis.types import Announcement, HourInfo, SchoolClass, TimetableChange, WebUntisData
from utils import tz


def announcement_from_dict(data: RawAnnouncementData) -> Announcement:
    return Announcement(data["subject"], data["body"])


def process_raw_untis_data(
    raw_untis_data: dict[dt.date, RawWebUntisData],
) -> dict[dt.date, WebUntisData]:
    clean_data: dict[dt.date, WebUntisData] = {}

    for date, raw_data in raw_untis_data.items():
        try:
            clean_data[date] = webuntisdata_from_raw(raw_data)
        except ValueError as e:
            warn(str(e))
            clean_data[date] = WebUntisData(date, [], [], "Montag", utils.now(), True)

    return clean_data


def webuntisdata_from_raw(data: RawWebUntisData) -> WebUntisData:
    date = dt.datetime.strptime(str(data["date"]), "%Y%m%d").astimezone(tz).date()
    ttchanges = [ttchange_from_row(row, date) for row in data["rows"]]
    announcements = list(map(announcement_from_dict, data["messageData"]["messages"]))

    return WebUntisData(
        date=date,
        changes=ttchanges,
        announcements=announcements,
        weekday=data["weekDay"],
        last_update=dt.datetime.strptime(data["lastUpdate"], "%d.%m.%Y %H:%M:%S").astimezone(tz),
        created_with_error=False,
    )


def ttchange_from_row(rowdata: RawTTChange, date: dt.date) -> TimetableChange:
    klass = SchoolClass.from_string(rowdata["group"])

    hours_str, lessonname, teacherinfo, status, message = rowdata["data"]

    hours = HourInfo.from_webuntis_string(hours_str)

    if klass == "Verw":
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
        lesson_canceled = True

    else:
        # if status isn't "Entfall" then add it to the end of the message string
        if status.strip() and message.strip():
            message += f" / {status}"
        elif status.strip() and not message.strip():
            message = status

        lesson_canceled = ["cancelStyle"] in rowdata["cellClasses"].values()

    message = parse_message(message, date)

    newteacher = strip_html(newteacher.upper().strip())
    originalteacher = strip_html(originalteacher.upper().strip())

    lessonname = parse_lesson_name(lessonname)

    return TimetableChange(
        date,
        klass,
        hours,
        lessonname,
        newteacher,
        message,
        lesson_canceled,
        originalteacher,
    )
