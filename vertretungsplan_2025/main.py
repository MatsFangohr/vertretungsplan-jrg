# ruff: noqa: E501
from __future__ import annotations

import datetime as dt
import logging
import platform
import re
import subprocess
import time
from typing import Callable, Self, TypedDict

import croniter
import minify_html
import requests
import requests_cache

from content import HTMLElements, SetupData

start_time = time.time()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def general_log(message: str, func: Callable[[str], None]) -> None:
    current_time = time.time()
    elapsed = current_time - start_time
    func(f"[{elapsed:05.3f}s] {message}")


def warn(message: str) -> None:
    general_log(message, logger.warning)


def info(message: str) -> None:
    general_log(message, logger.info)


info("dependencies loaded.")


class WebUntisManager:
    session: requests_cache.CachedSession

    def __init__(self: Self):
        self.session = requests_cache.CachedSession(
            "/home/ubuntu/vertretungsplan/vertretungsplan_2025/webcache",
            expire_after=300,
            backend="filesystem",
        )

    def get_data(self: Self, date: dt.date) -> requests.Response:
        payload = {"date": int(date.strftime("%Y%m%d"))} | SetupData.BASE_PAYLOAD
        return self.session.post(
            "https://samos.webuntis.com/WebUntis/monitor/substitution/data?school=rist2024",
            json=payload,
        )


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

    def __init__(  # noqa: PLR0913
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
        self.teacher = TimetableChange.strip_html(teacher.upper().strip())
        self.originalteacher = TimetableChange.strip_html(
            originalteacher.upper().strip()
        )

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
    def from_row(cls, rowdata: WebUntisRow) -> TimetableChange:
        # grab class
        klasse = rowdata["group"]

        hours, lessonname, teacherinfo, status, message = rowdata["data"]

        # teacherinfo is either 'AB' or 'AB, CD, EF'or 'AB (CD)' or 'AB, CD (EF)'
        split_info = teacherinfo.split("(")
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

        return cls(
            hours, klasse, lessonname, newteacher, originalteacher, message, entfall
        )

    def __repr__(self: Self) -> str:
        base = "[c] " if self.canceled else ""
        return base + f"{self.klasse} | {self.repr_stripped()}"

    # quite crude but does the job
    @staticmethod
    def strip_html(data: str) -> str:
        return re.sub("<[^>]+>", "", data)

    def repr_stripped(self: Self) -> str:
        return TimetableChange.strip_html(self.repr_html())

    def repr_html(self: Self) -> str:  # noqa: C901, PLR0912
        out = ""
        if self.canceled:
            if self.teacher:
                if self.lessonname:
                    out += f"{self.hours}. Stunde: {self.lessonname} bei {self.teacher} <b>fällt aus</b>"
                else:
                    out += f"{self.hours}. Stunde bei {self.teacher} fällt aus"
            else:  # noqa: PLR5501
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
                        out += f"{self.hours}. Stunde: {self.lessonname} bei {self.teacher} <span style='color: {SetupData.get_color(self.year, 'dark')}'>statt {self.originalteacher}</span>"
                    else:
                        out += f"{self.hours}. Stunde: {self.lessonname} bei {self.teacher}"
                else:  # noqa: PLR5501
                    if self.originalteacher:
                        out += f"{self.hours}. Stunde bei {self.teacher} <span style='color: {SetupData.get_color(self.year, 'dark')}'>statt {self.originalteacher}</span>"
                    else:
                        out += f"{self.hours}. Stunde bei {self.teacher}"
            else:  # noqa: PLR5501
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
        elif message.strip() == "AA @ home":
            return "Aufgaben (zuhause)"
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
                raise ValueError(f"invalid klasse: {klasse}!")
        return (year, klasse[-1])


class AnnouncementData(TypedDict):
    subject: str
    body: str


class AnnouncementsData(TypedDict):
    messages: list[AnnouncementData]


class WebUntisRow(TypedDict):
    data: tuple[str, str, str, str, str]
    group: str


class WebUntisData(TypedDict):
    date: str
    rows: list[WebUntisRow]
    messageData: AnnouncementsData
    weekDay: str


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


class VertretungsplanHTMLFiles(TypedDict):
    main: str
    about: str


class FormattingData(TypedDict):
    last_change: dt.datetime


class VertretungsplanFormatter:
    """Do not instantiate outside of the class. Only call via `generate_html_files`."""

    footer_data: FormattingData | None
    next_div_id = 1

    def __init__(self: Self):
        pass

    def generate_header(self: Self, startpage: int, text_color: str) -> str:
        return HTMLElements.HEAD_TEMPLATE.replace(
            "{{startpage}}", str(startpage)
        ).replace("{{textcolor}}", text_color)

    def generate_footer(
        self: Self, last_change: dt.datetime, next_update: dt.datetime
    ) -> str:
        dt_format = "%d.%m.%Y, %H:%M"

        return (
            HTMLElements.FOOTER_TEMPLATE.replace(
                "{{letzteänderung}}", last_change.strftime(dt_format)
            )
            .replace("{{letzteakt}}", dt.datetime.now().strftime(dt_format))
            .replace("{{nächsteakt}}", next_update.strftime(dt_format))
        )

    def create_background_color_div(self: Self, year: int) -> str:
        color = SetupData.get_color(year, "pale")
        return f"""<div class="colorblock" style="background-color: {color}">"""

    def generate_announcements(self: Self, data: list[AnnouncementData]) -> str:
        if data:
            html = self.create_background_color_div(0)
            for message in data:
                html += f"""<div class="announcement">{HTMLElements.ANNOUNCE_ICON}<div class="announce-text">"""
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

    def generate_day_div(
        self: Self, date: dt.date, webuntis_data: WebUntisData, div_active: bool
    ) -> str:
        rows: list[TimetableChange] = []

        for row in webuntis_data["rows"]:
            try:
                tt_change = TimetableChange.from_row(row)
            except ValueError as e:
                warn(str(e))
            else:
                rows.append(tt_change)

        rows.sort(key=lambda r: (r.year, r.classletter))

        page_title = f"""Vertretungsplan für {SetupData.WEEKDAYS[date.weekday()]}, den {date.strftime("%d.%m.%Y")}"""

        announcements = self.generate_announcements(
            webuntis_data["messageData"]["messages"]
        )

        out = f"""<div class="{"daywrapper active" if div_active else "daywrapper"}" id="{VertretungsplanFormatter.next_div_id}"><h1>{page_title}</h1><hr>{announcements}"""
        VertretungsplanFormatter.next_div_id += 1
        if webuntis_data["weekDay"] != SetupData.WEEKDAYS[date.weekday()]:
            out += """<span style="display: table; margin: 0 auto; padding: 1rem;">Keine Daten verfügbar. Das liegt an der Schule, nicht an dieser Webseite.</span></div></div>"""
            return out

        if not rows:
            out += """<span style="display: table; margin: 0 auto; padding: 1rem;">keine Daten bisher.</span></div>"""
            return out

        year_group = rows[0].year
        out += self.create_background_color_div(year_group)
        while len(rows) > 0:
            # if year changed
            if rows[0].year != year_group:
                out += f"""</div><hr>{self.create_background_color_div(rows[0].year)}"""
                year_group = rows[0].year

            # first collect all rows related to the next class
            current_class = rows[0].klasse
            firstrow = rows.pop(0)
            current_class_rows = [firstrow]

            while len(rows) > 0:
                if rows[0].klasse == current_class:
                    current_class_rows.append(rows.pop(0))
                else:
                    break

            # then format them accordingly
            out += f"<h2>{current_class}</h2>\n<p>"
            if "Klassenfahrt" in firstrow.message:
                out += f"Klassenfahrt mit {firstrow.teacher}</p>"
                continue

            for ttchange in current_class_rows:
                out += ttchange.repr_html() + "<br>"

            out += "</p>"
        out += "</div></div>"

        return out

    def generate_index_file(self: Self, dates: list[dt.date]) -> str:
        """Generates the main website file.

        @param dates May not be empty."""
        if dates == []:
            raise ValueError("dates may not be empty!")

        info("contacting webuntis...")

        day_divs: list[str] = []
        """Contains the html <divs>, one for each day."""

        # strip weekends
        dates = [d for d in dates if d.weekday() <= 4]

        # determine active page
        today = dt.date.today()
        tomorrow = today + dt.timedelta(days=1)

        active = [False] * len(dates)
        if today in dates and tomorrow in dates or today.weekday() == 4:
            if dt.datetime.now() > dt.datetime.combine(
                dt.date.today(), dt.time(14, 30)
            ):
                active[1] = True
            else:
                active[0] = True
        else:
            active[0] = True

        last_update_global = dt.datetime(1970, 1, 1)

        untis = WebUntisManager()

        for date in dates:
            webuntis_data = untis.get_data(date).json()["payload"]
            new_div = self.generate_day_div(
                date, webuntis_data, div_active=active.pop(0)
            )

            day_divs.append(new_div)

            last_update = dt.datetime.strptime(
                webuntis_data["lastUpdate"], "%d.%m.%Y %H:%M:%S"
            )
            last_update_global = max(last_update_global, last_update)

            info(f"generated {len(day_divs)} of {len(dates)} days")

        self.footer_data = {"last_change": last_update_global}

        next_update_time = croniter.croniter(
            SetupData.CRON_SPEC, dt.datetime.now()
        ).get_next(dt.datetime)

        main_element = "<main>" + "".join(day_divs) + "</main>"

        return (
            self.generate_header(startpage=0, text_color=SetupData.TEXT_COLOR)
            + HTMLElements.BUTTONS
            + main_element
            + self.generate_footer(
                last_change=last_update_global,
                next_update=next_update_time,
            )
        )

    def generate_about_page(self: Self) -> str:
        "Can only run successfully if generate_index_file has already been called with a non-empty"
        "dates list. Throws ValueError otherwise."
        if self.footer_data is None:
            raise ValueError(
                "Can only call `generate_about_page` after calling `generate_index_file` with a nontrivial date list!"
            )

        next_update_time = croniter.croniter(
            SetupData.CRON_SPEC, dt.datetime.now()
        ).get_next(dt.datetime)

        return (
            self.generate_header(startpage=0, text_color=SetupData.TEXT_COLOR)
            + HTMLElements.ABOUT_TEXT
            + self.generate_footer(
                last_change=self.footer_data["last_change"],
                next_update=next_update_time,
            )
        )

    @classmethod
    def generate_html_files(cls, dates: list[dt.date]) -> VertretungsplanHTMLFiles:
        """Generates main and about html files.

        @param dates May not be empty.
        """
        formatter = cls()

        return {
            "main": formatter.generate_index_file(dates),
            "about": formatter.generate_about_page(),
        }


def main() -> None:
    files = VertretungsplanFormatter.generate_html_files(
        [dt.date.today() + dt.timedelta(days=i) for i in range(7)]
    )

    out, about = files["main"], files["about"]

    minified_out = minify_html.minify(out, minify_css=True)

    write_out_and_copy(minified_out, about)

    info("done!")


if __name__ == "__main__":
    main()
