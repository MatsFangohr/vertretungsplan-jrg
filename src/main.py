# ruff: noqa: E501
from __future__ import annotations

import asyncio
import datetime as dt
import logging
import platform
import re
import subprocess
import time
from collections.abc import Callable
from typing import Literal, Self, TypedDict

import aiohttp
import croniter
import minify_html

from content import HTMLElements, SetupData, get_holiday, is_in_holiday

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


def get_soonest_weekday() -> dt.date:
    return {
        0: dt.date.today(),
        1: dt.date.today(),
        2: dt.date.today(),
        3: dt.date.today(),
        4: dt.date.today(),
        5: dt.date.today() + dt.timedelta(days=2),
        6: dt.date.today() + dt.timedelta(days=1),
    }[dt.date.today().weekday()]


info("dependencies loaded.")


class WebUntisManagerAsync:
    url: str

    def __init__(self):
        self.url = "https://samos.webuntis.com/WebUntis/monitor/substitution/data?school=rist2024"

    async def get_data(self, session: aiohttp.ClientSession, date: dt.date):
        payload = {"date": int(date.strftime("%Y%m%d"))} | SetupData.BASE_PAYLOAD
        async with session.post(self.url, json=payload) as r:
            return await r.json()

    async def get_multiple(self, dates) -> dict[dt.date, WebUntisData]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_data(session, d) for d in dates]
            results = await asyncio.gather(*tasks)
        return dict(zip(dates, results, strict=True))


class HourInfo:
    data: str
    needs_suffix: bool

    def __init__(self: Self, data: str, needs_suffix: bool = True) -> None:
        self.data = data.strip()
        try:
            if mat := re.match(r"^(\d+) - (\d+)$", self.data):
                self.start = int(mat.group(1))
                self.end = int(mat.group(2))
                assert self.start < self.end
            elif re.match(r"^\d+$", self.data):
                self.start = self.end = int(self.data)
            else:
                self.start = self.end = 0
                warn(f"unrecognized time format: '{data}'!")
        except ValueError:
            warn(f"invalid time format: '{data}'!")

        self.needs_suffix = needs_suffix

    @classmethod
    def from_data(cls, data: str, needs_suffix: bool, start: int, end: int) -> HourInfo:
        hourinfo = HourInfo("1", needs_suffix)
        hourinfo.data = data
        hourinfo.start = start
        hourinfo.end = end

        return hourinfo

    def parse_data(self: Self) -> HourInfo:
        HOUR_DATA = {
            "0 - 11": ("Ganztägig", 0, 0),
            "1 - 11": ("Ganztägig", 0, 0),
            "1 - 2": ("1. Block", 1, 2),
            "3 - 4": ("2. Block", 3, 4),
            "5 - 6": ("3. Block", 5, 6),
            "8 - 9": ("4. Block", 8, 9),
            "10 - 11": ("5. Block", 10, 11),
        }

        if self.data in HOUR_DATA:
            return HourInfo.from_data(
                HOUR_DATA[self.data][0],
                False,
                HOUR_DATA[self.data][1],
                HOUR_DATA[self.data][2],
            )

        return self

    def to_string(self: Self) -> str:
        if self.needs_suffix:
            return self.data + ". Stunde"
        else:
            return self.data

    def to_sorttuple(self: Self) -> tuple[int, int]:
        return (self.start, self.end)


class TimetableChange:
    hours: HourInfo
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
        hours: HourInfo,
        klasse: str,
        lessonname: str,
        teacher: str,
        originalteacher: str,
        message: str,
        canceled: bool,
    ) -> None:
        self.canceled = canceled

        self.hours = hours
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

        hours_str, lessonname, teacherinfo, status, message = rowdata["data"]

        hours = HourInfo(hours_str).parse_data()

        if klasse == "Verw":
            newteacher = ", ".join(
                filter(
                    lambda teacher: teacher != "",
                    re.sub(
                        "\\([^)]+\\)",
                        "",
                        (
                            TimetableChange.strip_html(teacherinfo)
                            .replace("-", "")
                            .replace(",", "")
                        ),
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
        hours = self.hours.to_string()
        if self.canceled:
            if self.teacher:
                if self.lessonname:
                    out += f"{hours}: {self.lessonname} bei {self.teacher} <b>fällt aus</b>"
                else:
                    out += f"{hours} bei {self.teacher} fällt aus"
            else:  # noqa: PLR5501
                if self.lessonname:
                    out += f"{hours} ({self.lessonname}) fällt aus"
                else:
                    out += f"{hours} fällt aus"
            if self.message:
                out += f": {self.message}"
        else:
            if self.teacher:
                if self.lessonname:
                    if self.originalteacher:
                        out += f"{hours}: {self.lessonname} bei {self.teacher} <span style='color: {SetupData.get_color(self.year, 'dark')}'>statt {self.originalteacher}</span>"
                    else:
                        out += f"{hours}: {self.lessonname} bei {self.teacher}"
                else:  # noqa: PLR5501
                    if self.originalteacher:
                        out += f"{hours} bei {self.teacher} <span style='color: {SetupData.get_color(self.year, 'dark')}'>statt {self.originalteacher}</span>"
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
        """only replaces 'AA' with 'Aufgaben'"""
        stripped_message = message.replace(" ", "").strip()
        if stripped_message == "AA":
            return "Aufgaben"
        elif stripped_message == "AA@home":
            return "Aufgaben (zuhause)"
        elif stripped_message == "Desy":
            return "DESY"
        else:
            REPLACEMENTS = {
                "f.a.": "fällt aus",
                "LaaO": "Lernen am anderen Ort",
            }
            for keyword, replacement in REPLACEMENTS.items():
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
    lastUpdate: str


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
    next_div_id = 0

    def __init__(self: Self) -> None:
        pass

    def generate_header(
        self: Self,
        startpage: int,
        text_color: str,
        last_change: dt.datetime,
        next_update: dt.datetime,
    ) -> str:
        header = HTMLElements.HEAD_TEMPLATE
        for placeholder, replacement in [
            ("letzteänderungTimestamp", str(last_change.timestamp())),
            ("letzteaktTimestamp", str(dt.datetime.now().timestamp())),
            ("nächsteaktTimestamp", str(next_update.timestamp())),
            ("startpage", str(startpage)),
            ("textcolor", text_color),
            (
                "title",
                "JRG Vertretungsplan"
                if platform.system() == "Linux"
                else "[DEBUG] Vertretungsplan",
            ),
            (
                "reloadIfRequired",
                HTMLElements.RELOAD_IF_REQUIRED_FUNCTION
                if platform.system() == "Linux"
                else "",
            ),
        ]:
            header = header.replace("{{" + placeholder + "}}", replacement)
            header = header.replace("\n        ", "\n")
        return header

    def generate_footer(
        self: Self, last_change: dt.datetime, next_update: dt.datetime
    ) -> str:
        dt_format = "%d.%m.%Y, %H:%M"

        footer = HTMLElements.FOOTER_TEMPLATE
        for keyword, replacement in [
            ("letzteänderung", last_change.strftime(dt_format)),
            ("letzteakt", dt.datetime.now().strftime(dt_format)),
            ("nächsteakt", next_update.strftime(dt_format)),
        ]:
            footer = footer.replace("{{" + keyword + "}}", replacement)
        return footer

    def create_background_color_div(self: Self, year: int) -> str:
        color = SetupData.get_color(year, "pale")
        return f"""<div class="colorblock" style="background-color: {color}">"""

    def generate_icon_block(self: Self, icon: str, subject: str, body: str) -> str:
        html = f"""<div class="announcement">{icon}<div class="announce-text">"""
        if subject and body:
            html += f"<h3>{subject}</h3><p>{body}</p>"
        elif subject:
            html += f"<h3>Ankündigung:</h3><p>{subject}</p>"
        elif body:
            html += f"<h3>Ankündigung:</h3><p>{body}</p>"
        else:
            html += ""

        html += "</div></div>"

        return html

    def generate_announcements(self: Self, data: list[AnnouncementData]) -> str:
        if data:
            html = self.create_background_color_div(0)
            for message in data:
                html += self.generate_icon_block(
                    HTMLElements.ANNOUNCE_ICON,
                    message["subject"].strip(),
                    message["body"].strip(),
                )
            return html + "</div><hr>"
        else:
            return ""

    def generate_day_div(
        self: Self, date: dt.date, webuntis_data: WebUntisData, div_active: bool
    ) -> str:
        rows: list[TimetableChange] = []

        encountered_error = False
        for row in webuntis_data["rows"]:
            try:
                tt_change = TimetableChange.from_row(row)
            except ValueError as e:
                encountered_error = True
                warn(str(e))
            else:
                rows.append(tt_change)

        rows.sort(key=lambda r: (r.year, r.classletter, r.hours.to_sorttuple()))

        page_title = f"""Vertretungsplan für {SetupData.WEEKDAYS[date.weekday()]}, den {date.strftime("%d.%m.%Y")}"""

        announcements = self.generate_announcements(
            webuntis_data["messageData"]["messages"]
        )

        out = f"""<div class="{"daywrapper active" if div_active else "daywrapper"}" id="{VertretungsplanFormatter.next_div_id}"><div class="title-block colorblock"><h1>{page_title}</h1></div><hr>"""
        VertretungsplanFormatter.next_div_id += 1
        if webuntis_data["weekDay"] != SetupData.WEEKDAYS[date.weekday()] or str(
            webuntis_data["date"]
        ) != date.strftime("%Y%m%d"):
            if is_in_holiday(date):
                holiday = get_holiday(date)
                out += f"""<span style="display: table; margin: 0 auto; padding: 1rem;">Es sind {holiday["name"]}! Die Schule beginnt am {SetupData.WEEKDAYS[holiday["first_day_after"].weekday()]}, dem {holiday["first_day_after"].strftime("%d.%m.%Y")} wieder. Wahrscheinlich kann man den Vertretungsplan mit dem Knopf unten schon einsehen.</span></div></div>"""
            else:
                out += """<span style="display: table; margin: 0 auto; padding: 1rem;">Keine Daten verfügbar.</span></div></div>"""
            return out
        else:
            out += announcements
            if encountered_error:
                error_warning = self.create_background_color_div(0)
                error_warning += self.generate_icon_block(
                    HTMLElements.WARN_ICON,
                    "Fehler bei der Datenverarbeitung!",
                    """Es kann sein, dass manche Einträge fehlen. Schaut sicherheitshalber bei <a style="color: unset; padding: unset;" href="https://samos.webuntis.com/WebUntis/monitor?school=rist2024&monitorType=subst&format=itslearning">WebUntis</a> nach. Schreibt Mats gerne, dann ist der Fehler bald weg. Wahrscheinlich hat WebUntis wieder das Format geändert.""",
                )
                error_warning += "</div><hr>"
                out += error_warning

        if not rows:
            out += """<span style="display: table; margin: 0 auto; padding: 1rem;">Keine Vertretungen bisher.</span></div>"""
            return out

        affected_classes = set(row.klasse for row in rows)
        unaffected_classes = [
            c for c in SetupData.ALL_CLASSES if c not in affected_classes
        ]

        if unaffected_classes and div_active:
            out += (
                self.create_background_color_div(-1)
                + "<h2>Klassen ohne Veränderung"
                + "".join(
                    map(
                        lambda cls: f"""<span id="klasse-{cls}"></span>""",
                        unaffected_classes,
                    )
                )
                + "</h2><p>"
                + ", ".join(unaffected_classes)
                + "</p></div><hr>"
            )

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
            out += "<h2"
            if div_active:
                out += f" id=klasse-{current_class}"
            out += f""">{current_class}"""
            if div_active:
                out += f"""<a href="#{current_class}" style="padding: unset;"><svg viewBox="0 0 576 512" class="link-icon-svg"><use href="#link-icon"/></svg></a>"""
            out += """</h2><p>"""
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
        startpage = 0
        if today in dates and tomorrow in dates or today.weekday() == 4:
            if dt.datetime.now() > dt.datetime.combine(
                dt.date.today(), dt.time(14, 30)
            ):
                active[1] = True
                startpage = 1
            else:
                active[0] = True
        else:
            active[0] = True

        last_update_global = dt.datetime(1970, 1, 1)

        untis = WebUntisManagerAsync()

        untis_data: dict[dt.date, dict[Literal["payload"], WebUntisData]] = asyncio.run(
            untis.get_multiple(dates)  # type: ignore
        )

        for date in dates:
            webuntis_data = untis_data[date]["payload"]
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
        ).get_next(dt.datetime) + dt.timedelta(seconds=8)

        main_element = "<main>" + "".join(day_divs) + "</main>"

        return (
            self.generate_header(
                startpage=startpage,
                text_color=SetupData.TEXT_COLOR,
                last_change=last_update_global,
                next_update=next_update_time,
            )
            + HTMLElements.LINK_ICON_DEF
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
        ).get_next(dt.datetime) + dt.timedelta(seconds=8)

        return (
            self.generate_header(
                startpage=0,
                text_color=SetupData.TEXT_COLOR,
                last_change=self.footer_data["last_change"],
                next_update=next_update_time,
            )
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


def select_dates() -> list[dt.date]:
    if is_in_holiday(dt.date.today()):
        return [get_soonest_weekday(), get_holiday(dt.date.today())["first_day_after"]]
    else:
        return [dt.date.today() + dt.timedelta(days=i) for i in range(7)]


def main() -> None:
    files = VertretungsplanFormatter.generate_html_files(select_dates())

    out, about = files["main"], files["about"]

    minified_out = minify_html.minify(out, minify_css=True)

    write_out_and_copy(minified_out, about)

    info("done!")


if __name__ == "__main__":
    main()
