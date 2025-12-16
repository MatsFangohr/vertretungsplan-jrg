# ruff: noqa: E501
import datetime as dt
import platform

import git

from base_types import HTML, SchoolClass, SchoolHoliday
from content import HTMLElements, SetupData
from untis import Announcement


def generate_title(
    title: str, letzteaenderung: dt.datetime, next_update: dt.datetime
) -> HTML:
    dt_format = "%d.%m.%Y, %H:%M"

    return f"""<div class="title-block colorblock">
    <div>
        <h1 style="margin-bottom: 0;">{title}</h1>
        <div style="container-type: inline-size;">
        <div class="centered-box-div cbd-flex cbd-flex-dynamic" style="margin-bottom: 0;">
            <span class="letzte-aenderung" class="cbd-flex-item">Stand: {letzteaenderung.strftime(dt_format)}</span>
            <span class="cbd-flex-item letzte-aktualisierung">Letzte Akt.: {dt.datetime.now().strftime(dt_format)}</span>
            <span class="cbd-flex-item naechste-aktualisierung">Nächste Akt.: {next_update.strftime(dt_format)}</span>
        </div></div>
    </div>
</div>"""


def generate_header(
    startpage: int,
    text_color: str,
    last_change: dt.datetime,
    next_update: dt.datetime,
) -> HTML:
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


def generate_footer(last_change: dt.datetime, next_update: dt.datetime) -> HTML:
    dt_format = "%d.%m.%Y, %H:%M"

    repo_location = (
        "/home/ubuntu/vertretungsplan"
        if platform.system() == "Linux"
        else "C:\\Users\\matsf\\github\\vertretungsplan"
    )
    repo = git.Repo(repo_location)
    ts = dt.datetime.fromtimestamp(repo.head.commit.committed_date)
    version_information = repo.git.describe("HEAD", tags=True, long=True)

    footer = HTMLElements.FOOTER_TEMPLATE
    for keyword, replacement in [
        ("letzteänderung", last_change.strftime(dt_format)),
        ("letzteakt", dt.datetime.now().strftime(dt_format)),
        ("nächsteakt", next_update.strftime(dt_format)),
        ("gitHash", f"{version_information} ({ts.strftime('%d.%m.%Y')})"),
    ]:
        footer = footer.replace("{{" + keyword + "}}", replacement)
    return footer


def create_background_color_div(year: int) -> HTML:
    color = SetupData.get_color(year, "pale")
    return f"""<div class="colorblock" style="background-color: {color}">"""


def generate_icon_block(icon: HTML, subject: str, body: str) -> HTML:
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


def generate_announcement_html(data: list[Announcement]) -> HTML:
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


def generate_error_message() -> HTML:
    error_warning = create_background_color_div(0)
    error_warning += generate_icon_block(
        HTMLElements.WARN_ICON,
        "Fehler bei der Datenverarbeitung!",
        HTMLElements.ERROR_MESSAGE,
    )
    error_warning += "</div><hr>"
    return error_warning


def generate_holiday_div(holiday: SchoolHoliday) -> HTML:
    return f"""<hr><span style="display: table; margin: 0 auto; padding: 1rem;">Es sind {holiday["name"]}! Die Schule beginnt am {SetupData.WEEKDAYS[holiday["first_day_after"].weekday()]}, dem {holiday["first_day_after"].strftime("%d.%m.%Y")} wieder. Wahrscheinlich kann man den Vertretungsplan mit dem Knopf unten schon einsehen.</span>"""


def generate_unaffected_classes_div(
    unaffected_classes: list[SchoolClass], is_active: bool
) -> HTML:
    def classes_to_string(cls: SchoolClass) -> str:
        return f"""<span id="klasse-{cls.to_string()}"></span>"""

    return (
        create_background_color_div(-1)
        + "<h2>Klassen ohne Veränderung"
        + "".join(
            map(
                classes_to_string,
                unaffected_classes,
            )
            if is_active
            else ""
        )
        + "</h2><p>"
        + ", ".join([cls.to_string() for cls in unaffected_classes])
        + "</p></div>"
    )
