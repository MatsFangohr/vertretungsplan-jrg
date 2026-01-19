import asyncio
import datetime as dt
import itertools
import subprocess
import sys
from collections.abc import Iterable

import minify_html

import config
from base_types import HTML, HTMLFiles, RawWebUntisData
from content import HTMLElements, SetupData
from html_gens import (
    create_background_color_div,
    generate_announcement_html,
    generate_error_message,
    generate_footer,
    generate_header,
    generate_holiday_div,
    generate_title,
    generate_unaffected_classes_div,
)
from logger import info, warn
from untis import WebUntisData, WebUntisManager
from utils import (
    get_holiday_data_from_date,
    get_next_update_time,
    get_soonest_weekday,
    get_weekday_str,
    is_in_holiday,
    tz,
)


def write_out_and_copy(index_html: HTML, about_html: HTML) -> None:
    info("writing out...")
    if "--test" in sys.argv:
        main_path = config.target_dir / "test.html"
    else:
        main_path = config.target_dir / "index.html"
    about_path = config.target_dir / "about.html"
    if "--debug" in sys.argv:
        with main_path.open("w+", encoding="utf-8") as f:
            f.write(index_html)
        with about_path.open("w+", encoding="utf-8") as f:
            f.write(about_html)
    else:
        with main_path.open("w+", encoding="utf-8") as f:
            f.write(index_html)

        with about_path.open("w+", encoding="utf-8") as f:
            f.write(about_html)

        if config.copy_command:
            info("copying to server...")
            subprocess.run(
                config.copy_command,
                shell=True,
                check=True,
            )


class VertretungsplanFormatter:
    """Do not instantiate outside of the class. Only call via `generate_html_files`."""

    next_div_id = 0

    def generate_day_div(
        self,
        date: dt.date,
        webuntis_data: WebUntisData,
        div_active: bool,
        show_unaffected_classes: bool,
        include_error_message: bool,
        last_update: dt.datetime,
        next_update: dt.datetime,
    ) -> HTML:
        changes = sorted(
            webuntis_data.changes,
            key=lambda r: (-1 * r.klasse.year, r.klasse.letter, r.hours.to_sorttuple()),
        )

        page_title = (
            f"""Vertretungsplan für {get_weekday_str(date)}, den {date.strftime("%d.%m.%Y")}"""
        )

        announcements = generate_announcement_html(webuntis_data.announcements)

        daywrapper_classes = "daywrapper active" if div_active else "daywrapper"
        element_id = VertretungsplanFormatter.next_div_id
        VertretungsplanFormatter.next_div_id += 1
        out = f"""<div class="{daywrapper_classes}" id="{element_id}">"""

        out += generate_title(page_title, last_update, next_update)

        if webuntis_data.weekday != get_weekday_str(date) or webuntis_data.date.strftime(
            "%Y%m%d"
        ) != date.strftime("%Y%m%d"):
            if is_in_holiday(date):
                holiday = get_holiday_data_from_date(date)
                out += generate_holiday_div(holiday)
                out += """</div></div>"""
            else:
                out += """<span style="display: table; margin: 0 auto; padding: 1rem;">Keine Daten verfügbar.</span></div></div>"""  # noqa: E501
            return out
        else:
            out += announcements
            if include_error_message:
                out += generate_error_message()

        if not changes:
            out += """<hr><span style="display: table; margin: 0 auto; padding: 1rem;">Keine Vertretungen bisher.</span></div>"""  # noqa: E501
            return out

        affected_classes = {row.klasse for row in changes}
        unaffected_classes = [c for c in SetupData.ALL_CLASSES if c not in affected_classes]

        if unaffected_classes and show_unaffected_classes:
            out += "<hr>" + generate_unaffected_classes_div(
                unaffected_classes, is_active=div_active
            )

        for year, year_changes in itertools.groupby(changes, lambda x: x.klasse.year):
            out += f"""<hr>{create_background_color_div(year)}"""

            for cls, cls_change_gen in itertools.groupby(year_changes, lambda x: x.klasse):
                cls_changes = list(cls_change_gen)
                out += "<h2"
                if div_active:
                    out += f" id=klasse-{cls.to_string()}"
                out += f""">{cls.to_string()}"""
                if div_active:
                    out += f"""<a href="#{cls.to_string()}" style="padding: unset;"><svg viewBox="0 0 576 512" class="link-icon-svg"><use href="#link-icon"/></svg></a>"""  # noqa: E501
                out += """</h2><p>"""
                if "Klassenfahrt" in cls_changes[0].message:
                    out += f"Klassenfahrt mit {cls_changes[0].teacher}</p>"
                    continue

                for ttchange in cls_changes:
                    out += ttchange.repr_html() + "<br>"

                out += "</p>"
            out += "</div>"
        out += "</div></div>"

        return out

    def get_raw_untis_data(self, dates: list[dt.date]) -> dict[dt.date, RawWebUntisData]:
        info("contacting webuntis...")
        return asyncio.run(WebUntisManager().get_multiple(dates))

    def process_untis_data(
        self, raw_untis_data: dict[dt.date, RawWebUntisData]
    ) -> dict[dt.date, WebUntisData]:
        untis_data: dict[dt.date, WebUntisData] = {}

        for date, raw_data in raw_untis_data.items():
            try:
                untis_data[date] = WebUntisData.from_raw_data(raw_data)
            except ValueError as e:
                warn(str(e))
                untis_data[date] = WebUntisData(date, [], [], "Montag", dt.datetime.now(tz), True)

        return untis_data

    def find_active_day(self, dates: list[dt.date]) -> dict[str, int]:
        today = dt.datetime.now(tz).date()
        tomorrow = today + dt.timedelta(days=1)

        if (today in dates and tomorrow in dates) or today.weekday() == 4:
            if dt.datetime.now(tz) > dt.datetime.combine(
                dt.datetime.now(tz).date(), dt.time(14, 30), tzinfo=tz
            ):
                return {"active_page": 1, "start_page": 1}
            else:
                return {"active_page": 0, "start_page": 0}
        else:
            return {"active_page": 0, "start_page": 0}

    def get_last_update_time(self, untis_data: Iterable[WebUntisData]) -> dt.datetime:
        return max(data.last_update for data in untis_data)

    def generate_index_file(
        self,
        dates: list[dt.date],
        untis_data: dict[dt.date, WebUntisData],
        last_update: dt.datetime,
    ) -> HTML:
        """Generates the main website file.

        @param dates May not be empty."""
        if not dates:
            raise ValueError("dates may not be empty!")

        day_divs: list[HTML] = []
        """Contains the html <divs>, one for each day."""

        # strip weekends
        dates = [d for d in dates if d.weekday() <= 4]

        # determine active page
        active_data = self.find_active_day(dates)

        next_update_time = get_next_update_time(
            SetupData.CRON_SPECS, dt.datetime.now(tz)
        ) + dt.timedelta(seconds=8)

        for n, date in enumerate(dates):
            new_div = self.generate_day_div(
                date,
                untis_data[date],
                div_active=active_data["active_page"] == n,
                show_unaffected_classes=active_data["active_page"] >= n,
                include_error_message=untis_data[date].created_with_error,
                last_update=last_update,
                next_update=next_update_time,
            )

            day_divs.append(new_div)

            info(f"generated {len(day_divs)} of {len(dates)} days")

        main_element = "<main>" + "".join(day_divs) + "</main>"

        return (
            generate_header(
                startpage=active_data["start_page"],
                last_change=last_update,
                next_update=next_update_time,
            )
            + HTMLElements.LINK_ICON_DEF
            + HTMLElements.NAVIGATION
            + HTMLElements.THEME_SWITCH_BUTTON
            + main_element
            + generate_footer()
        )

    def generate_about_page(self, last_update: dt.datetime) -> HTML:
        next_update_time = get_next_update_time(
            SetupData.CRON_SPECS, dt.datetime.now(tz)
        ) + dt.timedelta(seconds=8)

        return (
            generate_header(
                startpage=0,
                last_change=last_update,
                next_update=next_update_time,
            )
            + HTMLElements.THEME_SWITCH_BUTTON
            + HTMLElements.ABOUT_TEXT
            + generate_footer()
        )

    @classmethod
    def generate_html_files(cls, dates: list[dt.date]) -> HTMLFiles:
        """Generates main and about html files.

        @param dates May not be empty.
        """
        formatter = cls()

        untis_data = formatter.process_untis_data(formatter.get_raw_untis_data(dates))

        last_update = formatter.get_last_update_time(untis_data.values())

        return {
            "main": formatter.generate_index_file(dates, untis_data, last_update),
            "about": formatter.generate_about_page(last_update),
        }


def select_dates() -> list[dt.date]:
    today = dt.datetime.now(tz).date()
    if is_in_holiday(today):
        tomorrow = today + dt.timedelta(days=1)
        first_day_after_holidays = get_holiday_data_from_date(today)["first_day_after"]
        if not is_in_holiday(tomorrow):
            first_day = max(tomorrow, first_day_after_holidays)
            return [
                first_day,
                first_day + dt.timedelta(days=1),
            ]
        return [get_soonest_weekday(), first_day_after_holidays]
    else:
        candidates = [today + dt.timedelta(days=i) for i in range(7)]
        for i, date in enumerate(candidates):
            if is_in_holiday(date):
                return [*candidates[: i + 1], get_holiday_data_from_date(date)["first_day_after"]]
        return candidates


def main() -> None:
    info(f"starting processing at {dt.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}")

    files = VertretungsplanFormatter.generate_html_files(select_dates())

    out, about = files["main"], files["about"]

    minified_out = minify_html.minify(out, minify_css=True, minify_js=True)

    write_out_and_copy(minified_out, about)

    info("done!")


if __name__ == "__main__":
    main()
