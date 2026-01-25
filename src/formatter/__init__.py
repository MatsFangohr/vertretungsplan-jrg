from typing import Literal

from templates import HTML
from untis.types import TimetableChange


def get_color(klasse: int, tone: Literal["pale", "dark", "normal", "strong"]) -> str:
    if tone not in ["pale", "dark"]:
        raise ValueError("unsupported color!")
    if tone == "pale":
        return f"var(--year-color-{klasse})"
    else:  # tone must be dark
        return f"var(--year-color-{klasse}-intense)"


def format_ttchange(ttchange: TimetableChange) -> HTML:
    out = ""
    hours = ttchange.hours.to_string()
    if ttchange.canceled:
        if ttchange.teacher:
            if ttchange.lessonname:
                out += f"{hours}: {ttchange.lessonname} bei {ttchange.teacher}"
            else:
                out += f"{hours} bei {ttchange.teacher}"
        else:  # noqa: PLR5501
            if ttchange.lessonname:
                out += f"{hours} ({ttchange.lessonname})"
            else:
                out += f"{hours}"
        out += " <b>fällt aus</b>"
        if ttchange.message:
            out += f": {ttchange.message}"
    else:
        if ttchange.teacher:
            if ttchange.lessonname:
                if ttchange.originalteacher:
                    if "---" in ttchange.teacher:
                        out += f"{hours}: {ttchange.lessonname} bei {ttchange.teacher.replace('--- , ', '')} findet <span style='color: {get_color(ttchange.klasse.year, 'dark')}'>ohne {ttchange.originalteacher}</span> statt"  # noqa: E501
                    else:
                        out += f"{hours}: {ttchange.lessonname} bei {ttchange.teacher} <span style='color: {get_color(ttchange.klasse.year, 'dark')}'>statt {ttchange.originalteacher}</span>"  # noqa: E501
                else:
                    out += f"{hours}: {ttchange.lessonname} bei {ttchange.teacher}"
            else:  # noqa: PLR5501
                if ttchange.originalteacher:
                    out += f"{hours} bei {ttchange.teacher} <span style='color: {get_color(ttchange.klasse.year, 'dark')}'>statt {ttchange.originalteacher}</span>"  # noqa: E501
                else:
                    out += f"{hours} bei {ttchange.teacher}"
        else:  # noqa: PLR5501
            if ttchange.lessonname:
                out += f"{hours} ({ttchange.lessonname})"
            else:
                out += f"{hours}"
        if ttchange.message:
            out += f": {ttchange.message}"
    return out
