import datetime as dt
import itertools
from dataclasses import dataclass

import config
import formatter
import templates
import utils
from formatter.elements import (
    generate_announcement_html,
    generate_background_color_div,
    generate_error_message,
    generate_footer,
    generate_header,
    generate_holiday_div,
    generate_title,
    generate_unaffected_classes_div,
)
from formatter.utils import find_active_day
from logger import info
from templates import HTML
from untis.data import ALL_CLASSES, get_holiday_data_from_date, is_in_holiday
from untis.types import Announcement, TimetableChange, WebUntisData
from utils import get_next_update_time, get_weekday_str


@dataclass
class DayDivData:
    """Contains all data necessary to generate the <div> for a single day."""

    date: dt.date
    changes: list[TimetableChange]
    announcements: list[Announcement]
    div_active: bool
    show_unaffected_classes: bool
    encountered_parse_error: bool
    last_update: dt.datetime
    next_update: dt.datetime
    div_id: str
    is_valid: bool
    page_title: str


def create_day_div_data(
    date: dt.date,
    untis_data: WebUntisData,
    date_of_active_div: dt.date,
    encountered_parse_error: bool,
    last_update: dt.datetime,
    next_update: dt.datetime,
    div_id: str,
) -> DayDivData:
    div_valid = untis_data.weekday == get_weekday_str(date) and untis_data.date.strftime(
        "%Y%m%d"
    ) == date.strftime("%Y%m%d")
    page_title = f"""Vertretungsplan für {get_weekday_str(date)}, den {date.strftime("%d.%m.%Y")}"""

    changes = sorted(
        untis_data.changes,
        key=lambda r: (-1 * r.klass.year, r.klass.letter, r.hours.to_sorttuple()),
    )

    return DayDivData(
        date=date,
        changes=changes,
        announcements=untis_data.announcements,
        div_active=date_of_active_div == date,
        show_unaffected_classes=date_of_active_div >= date,
        encountered_parse_error=encountered_parse_error,
        last_update=last_update,
        next_update=next_update,
        div_id=div_id,
        is_valid=div_valid,
        page_title=page_title,
    )


def generate_day_div(data: DayDivData) -> HTML:
    """Contains or calls overall logic to generate the <div> for a single day."""
    date = data.date

    announcements = generate_announcement_html(data.announcements)

    daywrapper_classes = "daywrapper active" if data.div_active else "daywrapper"

    out = f"""<div class="{daywrapper_classes}" id="{data.div_id}">"""

    out += generate_title(data.page_title, data.last_update, data.next_update)

    if data.is_valid:
        out += announcements
        if data.encountered_parse_error:
            out += generate_error_message()
    else:
        if is_in_holiday(date):
            holiday = get_holiday_data_from_date(date)
            out += generate_holiday_div(holiday)
            out += """</div></div>"""
        else:
            out += """<span style="display: table; margin: 0 auto; padding: 1rem;">Keine Daten verfügbar.</span></div></div>"""  # noqa: E501
        return out

    if not data.changes:
        out += """<hr><span style="display: table; margin: 0 auto; padding: 1rem;">Keine Vertretungen bisher.</span></div>"""  # noqa: E501
        return out

    affected_classes = {row.klass for row in data.changes}
    unaffected_classes = [c for c in ALL_CLASSES if c not in affected_classes]

    if unaffected_classes and data.show_unaffected_classes:
        out += "<hr>" + generate_unaffected_classes_div(
            unaffected_classes, is_active=data.div_active
        )

    for year, year_changes in itertools.groupby(data.changes, lambda x: x.klass.year):
        out += f"""<hr>{generate_background_color_div(year)}"""

        for cls, cls_change_gen in itertools.groupby(year_changes, lambda x: x.klass):
            cls_changes = list(cls_change_gen)
            out += "<h2"
            if data.div_active:
                out += f" id=klasse-{cls.to_string()}"
            out += f""">{cls.to_string()}"""
            if data.div_active:
                out += f"""<a href="#{cls.to_string()}" style="padding: unset;"><svg viewBox="0 0 576 512" class="link-icon-svg"><use href="#link-icon"/></svg></a>"""  # noqa: E501
            out += """</h2><p>"""
            if "Klassenfahrt" in cls_changes[0].message:
                out += f"Klassenfahrt mit {cls_changes[0].teacher}</p>"
                continue

            for ttchange in cls_changes:
                out += formatter.format_ttchange(ttchange) + "<br>"

            out += "</p>"
        out += "</div>"
    out += "</div></div>"

    return out


def generate_index_file(
    untis_data: dict[dt.date, WebUntisData],
    last_update: dt.datetime,
) -> HTML:
    """Generates the main website file.

    `dates` may not be empty.
    """
    if not untis_data:
        raise ValueError("dates may not be empty!")

    day_divs: list[HTML] = []
    """Contains the html <divs>, one for each day."""

    # strip weekends
    dates = [date for date in untis_data if date.weekday() <= 4]

    # determine active page
    active_day = find_active_day(dates)

    next_update_time = get_next_update_time(config.cron_specs, utils.now()) + dt.timedelta(
        seconds=8
    )

    for n, date in enumerate(dates):
        div = generate_day_div(
            create_day_div_data(
                date=date,
                untis_data=untis_data[date],
                date_of_active_div=active_day,
                encountered_parse_error=untis_data[date].created_with_error,
                last_update=last_update,
                next_update=next_update_time,
                div_id=str(n),
            )
        )

        day_divs.append(div)

        info(f"generated {len(day_divs)} of {len(dates)} days")

    main_element = "<main>" + "".join(day_divs) + "</main>"

    return (
        generate_header(
            startpage=dates.index(active_day),
            last_change=last_update,
            next_update=next_update_time,
        )
        + templates.LINK_ICON_DEF
        + templates.NAVIGATION
        + templates.THEME_SWITCH_BUTTON
        + main_element
        + generate_footer()
    )


def generate_about_page(last_update: dt.datetime) -> HTML:
    next_update_time = get_next_update_time(config.cron_specs, utils.now()) + dt.timedelta(
        seconds=8
    )

    return (
        generate_header(
            startpage=0,
            last_change=last_update,
            next_update=next_update_time,
        )
        + templates.THEME_SWITCH_BUTTON
        + templates.ABOUT_TEXT
        + generate_footer()
    )
