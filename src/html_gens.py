# ruff: noqa: E501
import datetime as dt
import platform

from content import HTMLElements, SchoolClass, SchoolHoliday, SetupData
from untis import Announcement


def generate_header(
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
    return header


def generate_footer(last_change: dt.datetime, next_update: dt.datetime) -> str:
    dt_format = "%d.%m.%Y, %H:%M"

    footer = HTMLElements.FOOTER_TEMPLATE
    for keyword, replacement in [
        ("letzteänderung", last_change.strftime(dt_format)),
        ("letzteakt", dt.datetime.now().strftime(dt_format)),
        ("nächsteakt", next_update.strftime(dt_format)),
    ]:
        footer = footer.replace("{{" + keyword + "}}", replacement)
    return footer


def create_background_color_div(year: int) -> str:
    color = SetupData.get_color(year, "pale")
    return f"""<div class="colorblock" style="background-color: {color}">"""


def generate_icon_block(icon: str, subject: str, body: str) -> str:
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


def generate_announcement_html(data: list[Announcement]) -> str:
    if data:
        html = "<hr>" + create_background_color_div(0)
        for message in data:
            html += generate_icon_block(
                HTMLElements.ANNOUNCE_ICON,
                message.subject.strip(),
                message.body.strip(),
            )
        return html + "</div>"
    else:
        return ""


def generate_error_message() -> str:
    error_warning = create_background_color_div(0)
    error_warning += generate_icon_block(
        HTMLElements.WARN_ICON,
        "Fehler bei der Datenverarbeitung!",
        HTMLElements.ERROR_MESSAGE,
    )
    error_warning += "</div><hr>"
    return error_warning


def generate_holiday_div(holiday: SchoolHoliday) -> str:
    return f"""<span style="display: table; margin: 0 auto; padding: 1rem;">Es sind {holiday["name"]}! Die Schule beginnt am {SetupData.WEEKDAYS[holiday["first_day_after"].weekday()]}, dem {holiday["first_day_after"].strftime("%d.%m.%Y")} wieder. Wahrscheinlich kann man den Vertretungsplan mit dem Knopf unten schon einsehen.</span>"""


def generate_unaffected_classes_div(unaffected_classes: list[SchoolClass]) -> str:
    return (
        create_background_color_div(-1)
        + "<h2>Klassen ohne Veränderung"
        + "".join(
            map(
                lambda cls: f"""<span id="klasse-{repr(cls)}"></span>""",
                unaffected_classes,
            )
        )
        + "</h2><p>"
        + ", ".join([cls.to_string() for cls in unaffected_classes])
        + "</p></div>"
    )
