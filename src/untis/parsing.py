import datetime as dt
import re

import utils
from logger import warn
from utils import get_weekday_str, tz


def strip_html(data: str) -> str:
    return re.sub("<[^>]+>", "", data)


def hour_to_name(hour: int) -> str:
    LUT = {
        1: "1. Block",
        3: "2. Block",
        5: "3. Block",
        8: "4. Block",
        10: "5. Block",
        2: "2. Stunde",
        4: "4. Stunde",
        6: "6. Stunde",
        7: "Mittagspause",
        9: "9. Stunde",
        11: "11. Stunde",
        12: "12. Stunde",
    }

    if hour in LUT:
        return LUT[hour]
    else:
        return f"{hour}. Stunde"


def is_start_of_block(hour: int) -> bool:
    return hour in [1, 3, 5, 8, 10]


def time_to_hour(time: dt.time) -> int | None:
    LUT = {
        "07:50": 1,
        "08:35": 2,
        "09:50": 3,
        "10:35": 4,
        "11:50": 5,
        "12:35": 6,
        "13:20": 7,
        "13:35": 7,
        "14:20": 8,
        "15:05": 9,
        "15:50": 10,
        "16:05": 11,
        "16:50": 12,
    }

    time_str = time.strftime("%H:%M")
    return LUT.get(time_str)


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
            .replace(year=utils.now().year)
            .astimezone(tz)
            .date()
        )
        if date.month == 1 and utils.now().month == 12:
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


LESSON_NAMES = {
    "Mat": "Mathe",
    "Eng": "Englisch",
    "Deu": "Deutsch",
    "Lat": "Latein",
    "Franz": "Französisch",
    "Frz": "Französisch",
    "Phy": "Physik",
    "Mus": "Musik",
    "Spo": "Sport",
    "Che": "Chemie",
    "Inf": "Informatik",
    "Sem": "Seminar",
    "Bio": "Bio",
    "Geo": "Erdkunde",
    "Ges": "Geschichte",
    "förCho": "Chor",
    "Ita": "Italienisch",
    "Rel": "Religion",
    "Kun": "Kunst",
    "FörKL": "Klassenleitung",
    "Phi": "Philosophie",
    "Swi": "Schwimmen",
    "DSp": "DSP",
    "WiP": "WiPo",
    "Men": "Men",
    "A15": "Schulleitungsrunde",
    "MusBläs": "Musik (Bläser)",
    "Lion": "Lion's Quest",
    "FuP": "Forschen und Präsentieren",
    "Spa": "Spanisch",
    "SoRMS": "Schule ohne Rassismus",
    "kRe": "katholische Religion",
    "Rob": "Roberta",
    "ImpThea WPU": "Improtheater",
    "DaZDEU 5": "DAZ Deutsch",
    "DaZDEU 6": "DAZ Deutsch",
    "DaZMAT 5": "DAZ Mathe",
    "DaZMAT 6": "DAZ Mathe",
    "DaZ": "DAZ",
    "Leg": "LRS",
    "AmM": "Art meets Music",
    "UuG": "Unternehmen und Gesellschaft",
    "ELZmo": "Eigenlernzeit",
    "ELZdi": "Eigenlernzeit",
    "ELZmi": "Eigenlernzeit",
    "ELZdo": "Eigenlernzeit",
    "ELZfr": "Eigenlernzeit",
    "Textil": "Textiles Werken",
    "UmuNa": "Umwelt und Nachhaltigkeit",
    "": "",
}


def parse_lesson_name(name: str) -> str:
    """expands lesson names and returns the short version if not found"""
    stripname = name.strip()
    if stripname in LESSON_NAMES:
        return LESSON_NAMES[stripname]
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
