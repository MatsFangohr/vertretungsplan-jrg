import datetime as dt
import sys

import git

import config
import formatter.utils
import templates
import utils
from templates import HTML
from untis.types import Announcement, SchoolClass, SchoolHoliday
from utils import get_weekday_str, tz


def generate_title(title: str, last_change: dt.datetime, next_update: dt.datetime) -> HTML:
    """Generates the HTML title block.

    `last_change` should be the time intended to be displayed as "Letzte Änderung"
    `next_update` should be the predicted next update time

    These times are included as static HTML - if the user has JavaScript enabled, they will be
    updated live with the values passed to the `generate_header` function.
    """
    dt_format = "%d.%m.%Y, %H:%M"

    return f"""<div class="title-block colorblock">
    <div style="flex-grow: 1;">
        <h1 style="margin-bottom: 0;">{title}</h1>
        <div style="container-type: inline-size;">
        <div class="centered-box-div cbd-flex cbd-flex-dynamic status-bar">
            <span class="cbd-flex-item letzte-aenderung">Letzte Änderung: {last_change.strftime(dt_format)}</span>
            <span class="cbd-flex-item letzte-aktualisierung">Letzte Akt.: {utils.now().strftime(dt_format)}</span>
            <span class="cbd-flex-item naechste-aktualisierung">Nächste Akt.: {next_update.strftime(dt_format)}</span>
        </div></div>
    </div>
</div>"""  # noqa: E501


def generate_header(
    startpage: int,
    last_change: dt.datetime,
    next_update: dt.datetime,
) -> HTML:
    """Generates the HTML header.

    `startpage` should be the 0-indexed number of the currently 'active' page. Page change buttons
    may not work correctly if set incorrectly.
    `last_change` should be the time intended to be displayed as "Letzte Änderung"
    `next_update` should be the predicted next update time

    These times will not be visible to users without JavaScript, but will be updated as a relative
    time (e.g. "vor 5 Minuten") by the page JavaScript.
    """
    header = templates.HEAD_TEMPLATE
    for placeholder, replacement in [
        ("letzteänderungTimestamp", str(last_change.timestamp())),
        ("letzteaktTimestamp", str(utils.now().timestamp())),
        ("nächsteaktTimestamp", str(next_update.timestamp())),
        ("startpage", str(startpage)),
        (
            "title",
            "[DEBUG] Vertretungsplan" if "--debug" in sys.argv else "JRG Vertretungsplan",
        ),
        (
            "reloadIfRequired",
            templates.RELOAD_IF_REQUIRED_FUNCTION if "--debug" not in sys.argv else "",
        ),
    ]:
        header = header.replace("{{" + placeholder + "}}", replacement)
    return header


def generate_footer() -> HTML:
    """Generates the HTML footer, including git version information. May throw errors if git
    information can't be found.
    """
    repo = git.Repo(config.BASE_PATH)
    ts = dt.datetime.fromtimestamp(repo.head.commit.committed_date, tz=tz)
    version_information = repo.git.describe("HEAD", tags=True, long=True)

    footer = templates.FOOTER_TEMPLATE
    for keyword, replacement in [
        ("gitHash", f"{version_information} ({ts.strftime('%d.%m.%Y')})"),
    ]:
        footer = footer.replace("{{" + keyword + "}}", replacement)
    return footer


def generate_background_color_div(year: int) -> HTML:
    color = formatter.utils.get_color(year, "pale")
    return f"""<div class="colorblock" style="background-color: {color}">"""


def generate_single_announce_block(icon: HTML, subject: str, body: str) -> HTML:
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
        html = "<hr>" + generate_background_color_div(0)
        for message in data:
            html += generate_single_announce_block(
                templates.ANNOUNCE_ICON,
                message.subject.strip(),
                message.body.strip(),
            )
        return html + "</div>"
    else:
        return ""


def generate_error_message() -> HTML:
    error_warning = generate_background_color_div(0)
    error_warning += generate_single_announce_block(
        templates.WARN_ICON,
        "Fehler bei der Datenverarbeitung!",
        templates.ERROR_MESSAGE,
    )
    error_warning += "</div><hr>"
    return error_warning


def generate_holiday_div(holiday: SchoolHoliday) -> HTML:
    return f"""<hr><span style="display: table; margin: 0 auto; padding: 1rem;">Es sind {holiday.name}! Die Schule beginnt am {get_weekday_str(holiday.first_day_after)}, dem {holiday.first_day_after.strftime("%d.%m.%Y")} wieder. Wahrscheinlich kann man den Vertretungsplan mit dem Knopf unten schon einsehen.</span>"""  # noqa: E501


def generate_unaffected_classes_div(unaffected_classes: list[SchoolClass], is_active: bool) -> HTML:
    def classes_to_string(cls: SchoolClass) -> str:
        return f"""<span id="klasse-{cls.to_string()}"></span>"""

    return (
        """<div class="colorblock" style="background-color: var(--unaffected-color)">"""
        "<h2>Klassen ohne Veränderung"
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
