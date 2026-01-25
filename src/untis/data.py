import datetime as dt

from untis.types import SchoolClass, SchoolHoliday

BASE_PAYLOAD = {
    "formatName": "itslearning",
    "schoolName": "rist2024",
    "dateOffset": 0,
    "strikethrough": False,
    "mergeBlocks": True,  # leave on
    "showOnlyFutureSub": False,  # show past
    "showBreakSupervisions": False,  # does nothing
    "showTeacher": True,
    "showClass": False,
    "showHour": True,
    "showInfo": True,
    "showRoom": False,  # only works for subjects with specific rooms
    "showSubject": True,
    "groupBy": 1,
    "hideAbsent": False,  # class trips
    "departmentIds": [],  # type: ignore
    "departmentElementType": 1,
    "hideCancelWithSubstitution": True,  # display replaced subjects as cancelled
    "hideCancelCausedByEvent": False,  # leave false
    "showTime": False,
    "showSubstText": True,
    "showAbsentElements": [],  # type: ignore
    "showAffectedElements": [1],
    "showUnitTime": False,
    "showMessages": True,
    "showStudentgroup": False,
    "enableSubstitutionFrom": False,  # disable skip to next day
    "showSubstitutionFrom": 1200,
    "showTeacherOnEvent": False,  # nothing
    "showAbsentTeacher": True,
    "strikethroughAbsentTeacher": False,
    "activityTypeIds": [],  # type: ignore
    "showEvent": True,
    "showCancel": True,
    "showOnlyCancel": False,
    "showSubstTypeColor": False,
    "showExamSupervision": True,
    "showUnheraldedExams": True,
}

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

ALL_CLASSES = [
    SchoolClass(year, letter)
    for year, letter in [
        (1, ""),
        (5, "a"),
        (5, "b"),
        (5, "c"),
        (5, "d"),
        (5, "e"),
        (6, "a"),
        (6, "b"),
        (6, "c"),
        (6, "d"),
        (6, "e"),
        (6, "f"),
        (7, "a"),
        (7, "b"),
        (7, "c"),
        (7, "d"),
        (7, "e"),
        (8, "a"),
        (8, "b"),
        (8, "c"),
        (8, "d"),
        (8, "e"),
        (9, "a"),
        (9, "b"),
        (9, "c"),
        (9, "d"),
        (9, "e"),
        (10, "a"),
        (10, "b"),
        (10, "c"),
        (10, "d"),
        (10, "e"),
        (10, "f"),
        (11, "a"),
        (11, "b"),
        (11, "c"),
        (11, "d"),
        (11, "e"),
        (12, "a"),
        (12, "b"),
        (12, "c"),
        (12, "d"),
        (12, "e"),
    ]
]


SCHOOL_HOLIDAYS: list[SchoolHoliday] = [
    {
        "name": "Winterferien",
        "start": dt.date(2025, 12, 19),
        "end": dt.date(2026, 1, 6),
        "first_day_after": dt.date(2026, 1, 7),
    },
    {
        "name": "Osterferien",
        "start": dt.date(2026, 3, 26),
        "end": dt.date(2026, 4, 10),
        "first_day_after": dt.date(2026, 4, 13),
    },
    {
        "name": "Pfingstferien",
        "start": dt.date(2026, 5, 13),
        "end": dt.date(2026, 5, 15),
        "first_day_after": dt.date(2026, 5, 18),
    },
    {
        "name": "Sommerferien",
        "start": dt.date(2026, 7, 5),
        "end": dt.date(2026, 8, 15),
        "first_day_after": dt.date(2026, 8, 17),
    },
]


HOLIDAY_DAYS: dict[dt.date, SchoolHoliday] = {}

for holiday in SCHOOL_HOLIDAYS:
    if holiday["end"] < holiday["start"]:
        raise ValueError("holiday must end after it begins!")
    current_date = holiday["start"]
    while current_date <= holiday["end"]:
        if current_date in HOLIDAY_DAYS:
            raise ValueError(f"date {current_date} is part of two holidays!")
        HOLIDAY_DAYS[current_date] = holiday
        current_date += dt.timedelta(days=1)

HOUR_DATA = {
    "0 - 11": ("Ganztägig", 0, 0),
    "1 - 6": ("1. bis 3. Block", 1, 6),
    "1 - 9": ("1. bis 4. Block", 1, 9),
    "1 - 11": ("Ganztägig", 0, 0),
    "1 - 2": ("1. Block", 1, 2),
    "3 - 4": ("2. Block", 3, 4),
    "5 - 6": ("3. Block", 5, 6),
    "8 - 9": ("4. Block", 8, 9),
    "10 - 11": ("5. Block", 10, 11),
    "2 - 11": ("Ab 2. Stunde", 2, 11),
    "3 - 11": ("Ab 2. Block", 3, 11),
    "4 - 11": ("Ab 4. Stunde", 4, 11),
    "5 - 11": ("Ab 3. Block", 5, 11),
    "6 - 11": ("Ab 6. Stunde", 6, 11),
    "8 - 11": ("Ab 4. Block", 8, 11),
    "9 - 11": ("Ab 9. Stunde", 9, 11),
}
