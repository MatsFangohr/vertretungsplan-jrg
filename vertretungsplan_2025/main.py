from __future__ import annotations

import datetime
import logging
import platform
import re
import subprocess
import time
from functools import cache
from typing import Callable, Self, TypedDict

import croniter
import minify_html
import requests
import requests_cache

from content import (
    ABOUT_TEXT,
    ANNOUNCE_ICON,
    BASE_PAYLOAD,
    BUTTONS,
    COLORS,
    CRON_SPEC,
    FOOTER_TEMPLATE,
    HEAD_TEMPLATE,
    LESSON_NAMES,
    TEXT_COLOR,
    WEEKDAYS,
)

start_time = time.time()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def general_log(message: str, func: Callable[[str], None]) -> None:
    current_time = time.time()
    elapsed = current_time - start_time
    func(f"[{elapsed:02.3f}s] {message}")


def warn(message: str) -> None:
    general_log(message, logger.warning)


def info(message: str) -> None:
    general_log(message, logger.info)


info("dependencies loaded.")

# display tomorrow by default?
# checks if the current time is past 16:15, as 5th block has started by then
SHOW_TOMORROW = datetime.datetime.now() > datetime.datetime.combine(
    datetime.date.today(), datetime.time(16, 15)
)

# cache session
session = requests_cache.CachedSession(
    "/home/ubuntu/vertretungsplan/vertretungsplan_2025/webcache",
    expire_after=599,
    backend="filesystem",
)


@cache
def get_data_from_webuntis(date: datetime.date) -> requests.Response:
    payload = {"date": int(date.strftime("%Y%m%d"))} | BASE_PAYLOAD
    return session.post(
        "https://samos.webuntis.com/WebUntis/monitor/substitution/data?school=rist2024",
        json=payload,
    )


# quite crude but does the job
def strip_html(data: str) -> str:
    return re.sub("<[^>]+>", "", data)


def create_background_color_div(year: int) -> str:
    color = COLORS[year]["pale"]
    return f"""<div class="colorblock" style="background-color: {color}">"""


def fill_footer_placeholders(last_update: datetime.datetime) -> str:
    dt_format = "%d.%m.%Y, %H:%M"

    cron = croniter.croniter(CRON_SPEC, datetime.datetime.now())
    return (
        FOOTER_TEMPLATE.replace("{{letzteänderung}}", last_update.strftime(dt_format))
        .replace("{{letzteakt}}", datetime.datetime.now().strftime(dt_format))
        .replace("{{nächsteakt}}", cron.get_next(datetime.datetime).strftime(dt_format))
    )


class Row(TypedDict):
    group: str
    data: tuple[str, str, str, str, str]


class TimetableChange:
    hours: str
    lessonname: str
    teacher: str
    message: str
    year: int
    classletter: str
    klasse: str
    canceled: bool
    originalteacher: str

    def __init__(
        self: Self,
        hours: str,
        klasse: str,
        lessonname: str,
        teacher: str,
        originalteacher: str,
        message: str,
        canceled: bool,
    ) -> None:
        self.canceled = canceled

        self.hours = hours.strip()
        self.klasse = klasse.strip()

        # teachers should be uppercase
        self.teacher = teacher.upper().strip()
        self.originalteacher = originalteacher.upper().strip()

        self.message = TimetableChange.parse_message(message)
        self.lessonname = TimetableChange.parse_lesson_name(lessonname)
        self.year, self.classletter = TimetableChange.parse_klasse(klasse)

        if not self.hours:
            raise ValueError("no hours!")
        if not self.year or not self.classletter:
            raise ValueError("no class!")
        if not self.teacher and not self.message:
            raise ValueError("needs either teacher or message!")

    @classmethod
    def from_row(cls, rowdata: Row) -> TimetableChange:
        # grab class
        klasse = rowdata["group"]

        hours, lessonname, teacherinfo, status, message = rowdata["data"]

        # teacherinfo is either 'AB' or 'AB, CD, EF'or 'AB (CD)' or 'AB, CD (EF)'
        split_info = strip_html(teacherinfo).split("(")
        match split_info:
            # case 'AB' or 'AB, CD, EF'
            case [teacher]:
                newteacher = teacher
                originalteacher = ""

            # case 'AB (CD)' or 'AB, CD (EF)'
            case [new, original]:
                newteacher = new
                originalteacher = original.strip(")")

            case _:
                raise ValueError(f"invalid teacherinfo: {split_info}!")

        # marker for ausfall
        if status.strip() == "Entfall":
            entfall = True
        else:
            entfall = False
            # if status isn't "ausfall" then add it to the end of the message string
            if status.strip() and message.strip():
                message += f" / {status}"
            elif status.strip() and not message.strip():
                message = status

        return cls(hours, klasse, lessonname, newteacher, originalteacher, message, entfall)

    def __repr__(self: Self) -> str:
        base = "[c] " if self.canceled else ""
        return base + f"{self.klasse} | {self.repr_stripped()}"

    def repr_stripped(self: Self) -> str:
        return strip_html(self.repr_html())

    def repr_html(self: Self) -> str:
        out = ""
        if self.canceled:
            if self.teacher:
                if self.lessonname:
                    out += f"{self.hours}. Stunde: {self.lessonname} bei {self.teacher} <b>fällt aus</b>"
                else:
                    out += f"{self.hours}. Stunde bei {self.teacher} fällt aus"
            else:
                if self.lessonname:
                    out += f"{self.hours}. Stunde ({self.lessonname}) fällt aus"
                else:
                    out += f"{self.hours}. Stunde fällt aus"
            if self.message:
                out += f": {self.message}"
        else:
            if self.teacher:
                if self.lessonname:
                    if self.originalteacher:
                        out += f"{self.hours}. Stunde: {self.lessonname} bei {self.teacher} statt {self.originalteacher}"
                    else:
                        out += f"{self.hours}. Stunde: {self.lessonname} bei {self.teacher}"
                else:
                    if self.originalteacher:
                        out += (
                            f"{self.hours}. Stunde bei {self.teacher} statt {self.originalteacher}"
                        )
                    else:
                        out += f"{self.hours}. Stunde bei {self.teacher}"
            else:
                if self.lessonname:
                    out += f"{self.hours}. Stunde ({self.lessonname})"
                else:
                    out += f"{self.hours}. Stunde"
            if self.message:
                out += f": {self.message}"
        return out

    @staticmethod
    def parse_message(message: str) -> str:
        """only replaces 'AA' with 'Aufgaben'"""
        if message.strip() == "AA":
            return "Aufgaben"
        return message

    @staticmethod
    def parse_lesson_name(name: str) -> str:
        """expands lesson names and returns the short version if not found"""
        stripname = name.strip()
        if stripname in LESSON_NAMES:
            return LESSON_NAMES[stripname]
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
                raise ValueError(f"invalid klasse: {klasse}!")
        return (year, klasse[-1])


def parse_announcements(data: list[dict[str, str]]) -> str:
    if data:
        html = create_background_color_div(0)
        for message in data:
            html += f"""<div class="announcement">{ANNOUNCE_ICON}<div class="announce-text">"""
            subject = message["subject"].strip()
            body = message["body"].strip()

            if subject and body:
                html += f"<h3>{subject}</h3><p>{body}</p>"
            elif subject:
                html += f"<h3>Ankündigung:</h3><p>{subject}</p>"
            elif body:
                html += f"<h3>Ankündigung:</h3><p>{body}</p>"
            else:
                html += ""

            html += "</div></div>"

        return html + "</div><hr>"
    else:
        return ""


def generate_div(date: datetime.date, div_id: int, active: bool) -> tuple[str, bool]:
    data = get_data_from_webuntis(date).json()

    rows: list[TimetableChange] = []

    for row in data["payload"]["rows"]:
        try:
            rows.append(TimetableChange.from_row(row))
        except ValueError as e:
            warn(str(e))

    title = f"""Vertretungsplan für {WEEKDAYS[date.weekday()]}, den {date.strftime("%d.%m.%Y")}"""

    announcements = parse_announcements(data["payload"]["messageData"]["messages"])

    rows.sort(key=lambda r: (r.year, r.classletter))

    out = f"""<div class="{"daywrapper active" if active else "daywrapper"}" id="{div_id}"><h1>{title}</h1><hr>{announcements}"""
    if data["payload"]["weekDay"] != WEEKDAYS[date.weekday()]:
        if active:
            return generate_div(date, div_id, False)
        out += """<span style="display: table; margin: 0 auto; padding: 1rem;">Keine Daten verfügbar. Das liegt an der Schule, nicht an dieser Webseite.</span></div></div>"""
        return out, active

    if rows:
        old_year = rows[0].year
        out += create_background_color_div(old_year)
        while len(rows) > 0:
            if rows[0].year != old_year:
                out += f"""</div><hr>{create_background_color_div(rows[0].year)}"""
                old_year = rows[0].year
            currentclass = rows[0].klasse
            currentrows = [rows.pop(0)]
            while len(rows) > 0:
                if rows[0].klasse == currentclass:
                    currentrows.append(rows.pop(0))
                else:
                    break
            out += f"<h2>{currentclass}</h2>\n<p>"
            for row in currentrows:
                out += row.repr_html() + "<br>"
            out += "</p>"
    else:
        out += """<span style="display: table; margin: 0 auto; padding: 1rem;">keine Daten bisher.</span>"""
    out += "</div></div>"

    return (out, active)


def generate_divs() -> tuple[list[str], datetime.datetime, int]:
    last_update_global = datetime.datetime(1970, 1, 1)

    divs = []

    info("contacting webuntis...")

    completed = 0

    dates = [datetime.date.today() + datetime.timedelta(days=i) for i in range(7)]

    dates = [d for d in dates if d.weekday() <= 4]

    active = [False] * len(dates)
    if SHOW_TOMORROW:
        active[1] = True
    else:
        active[0] = True

    for i, date in enumerate(dates):
        if date.weekday() <= 4:
            should_be_active = active[i]

            div, is_active = generate_div(date, i + 1, should_be_active)

            if should_be_active != is_active:
                # rotate list one to the right
                active = active[-1:] + active[:-1]

            divs.append(div)

            last_update = datetime.datetime.strptime(
                get_data_from_webuntis(date).json()["payload"]["lastUpdate"],
                "%d.%m.%Y %H:%M:%S",
            )
            last_update_global = max(last_update_global, last_update)
            completed += 1

            info(f"generated {completed} of {len(dates)} days")

    return divs, last_update_global, active.index(True) + 1


def write_out_and_copy(index_html: str, about_html: str) -> None:
    info("writing out...")
    if platform.system() == "Linux":
        with open("/var/www/html/index.html", "w+", encoding="utf-8") as f:
            f.write(index_html)

        with open("/var/www/html/about.html", "w+", encoding="utf-8") as f:
            f.write(about_html)

        info("copying to wilma...")
        subprocess.run(
            "scp -q -i /home/ubuntu/.ssh/id_wilma_auth /var/www/html/* mats@wilma:/home/mats/www-jrg",
            shell=True,
            check=True,
        )
    else:
        with open("index.html", "w+", encoding="utf-8") as f:
            f.write(index_html)


def main() -> None:
    divs, last_update_global, startpage = generate_divs()

    head = HEAD_TEMPLATE.replace("{{startpage}}", str(startpage)).replace(
        "{{textcolor}}", TEXT_COLOR
    )

    footer = fill_footer_placeholders(last_update_global)

    out = head + BUTTONS + "".join(divs) + footer
    about = head + ABOUT_TEXT + footer

    minified_out = minify_html.minify(out, minify_css=True)

    write_out_and_copy(minified_out, about)

    info("done!")


if __name__ == "__main__":
    main()
