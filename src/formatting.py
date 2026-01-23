import datetime as dt
import re

from content import SetupData
from logger import warn
from utils import get_weekday_str, hour_to_name, is_start_of_block, time_to_hour, tz


def parse_message(message: str, date_of_message: dt.date) -> str:
    stripped_message = message.replace(" ", "").strip()
    COMPLETE_REPLACEMENTS = {  # noqa: N806
        "AA": "Aufgaben",
        "AA@home": "Aufgaben (zuhause)",
        "Desy": "DESY",
    }

    if stripped_message in COMPLETE_REPLACEMENTS:
        message = COMPLETE_REPLACEMENTS[stripped_message]

    PARTIAL_REPLACEMENTS = {  # noqa: N806
        "f.a.": "fällt aus",
        "LaaO": "Lernen am anderen Ort",
    }

    for keyword, replacement in PARTIAL_REPLACEMENTS.items():
        message = message.replace(keyword, replacement)

    if mat := re.search(r"Verlegung (nach|von) (\d?\d\.\d?\d\.) \/ (\d?\d:\d\d)", message):
        date = (
            dt.datetime.strptime(mat.group(2), "%d.%m.")  # noqa: DTZ007 see two lines below
            .replace(year=dt.datetime.now(tz).year)
            .astimezone(tz)
            .date()
        )
        if date.month == 1 and dt.datetime.now(tz).month == 12:
            date = date.replace(year=date.year + 1)

        time = dt.datetime.strptime(mat.group(3), "%H:%M").time().replace(tzinfo=tz)  # noqa: DTZ007
        hour = time_to_hour(time)
        start_of_block = is_start_of_block(hour) if hour else None
        weekday_str = get_weekday_str(date)

        improved = ""

        if mat.group(1) == "nach":
            if date_of_message == date:
                improved += "Verlegt in "
                if hour:
                    if start_of_block:
                        improved += f"den {hour_to_name(hour)}"
                    else:
                        improved += f"die {hour_to_name(hour)}"
                else:
                    improved += f"verlegt nach {time.strftime('%H:%M')}"
            else:
                improved += f"Verlegt auf {weekday_str}, {date.strftime('%d.%m.%Y')} "
                if hour:
                    if start_of_block:
                        improved += f"im {hour_to_name(hour)}"
                    else:
                        improved += f"in der {hour_to_name(hour)}"
                else:
                    improved += time.strftime("%H:%M")
        elif mat.group(1) == "von":
            improved += "Verlegung "
            if hour:
                if start_of_block:
                    improved += f"aus dem {hour_to_name(hour)}"
                else:
                    improved += f"aus der {hour_to_name(hour)}"
            else:
                improved += f"von {time.strftime('%H:%M')}"
            if date_of_message != date:
                improved += f" vom {weekday_str}, {date.strftime('%d.%m.%Y')}"

        message = message.replace(mat.group(0), improved)
    return message


def parse_lesson_name(name: str) -> str:
    """expands lesson names and returns the short version if not found"""
    stripname = name.strip()
    if stripname in SetupData.LESSON_NAMES:
        return SetupData.LESSON_NAMES[stripname]
    else:
        warn(f"can't find lesson name: {name}")
        return stripname


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
