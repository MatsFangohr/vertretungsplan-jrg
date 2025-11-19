# ruff: noqa: E501, RUF012
import datetime as dt
from collections import defaultdict
from collections.abc import Mapping
from typing import Literal, TypedDict, cast


class ColorDict(TypedDict):
    pale: str
    dark: str
    normal: str
    strong: str


class SetupData:
    @staticmethod
    def get_color(klass: int, tone: Literal["pale", "dark", "normal", "strong"]) -> str:
        return SetupData.COLORS[klass][tone]

    BASE_PAYLOAD = {
        "formatName": "itslearning",
        "schoolName": "rist2024",
        "dateOffset": 0,
        "strikethrough": False,
        "mergeBlocks": True,  # leave on
        "showOnlyFutureSub": False,  # show past
        "showBreakSupervisions": False,  # nothing
        "showTeacher": True,
        "showClass": False,
        "showHour": True,
        "showInfo": True,
        "showRoom": False,  # nur sport physik bio
        "showSubject": True,
        "groupBy": 1,
        "hideAbsent": False,  # klassenfahrten
        "departmentIds": [],
        "departmentElementType": 1,
        "hideCancelWithSubstitution": True,  # ersetztes als ausgefallen anzeigen
        "hideCancelCausedByEvent": False,  # LEAVE FALSE
        "showTime": False,
        "showSubstText": True,
        "showAbsentElements": [],
        "showAffectedElements": [1],
        "showUnitTime": False,
        "showMessages": True,
        "showStudentgroup": False,
        "enableSubstitutionFrom": False,  # disable skip to next day
        "showSubstitutionFrom": 1200,
        "showTeacherOnEvent": False,  # nothing
        "showAbsentTeacher": True,
        "strikethroughAbsentTeacher": False,
        "activityTypeIds": [],
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
        "DaZMAT 6": "DAZ Mathe",
        "AmM": "Art meets Music",
        "UuG": "Unternehmen und Gesellschaft",
        "ELZmo": "Eigenlernzeit",
        "ELZdi": "Eigenlernzeit",
        "ELZmi": "Eigenlernzeit",
        "ELZdo": "Eigenlernzeit",
        "ELZfr": "Eigenlernzeit",
        "": "",
    }

    CRON_SPEC = "*/7 6-23 * * 0-5"

    TEXT_COLOR = "#000000"
    # TEXT_COLOR = "#111827"

    WEEKDAYS = {
        0: "Montag",
        1: "Dienstag",
        2: "Mittwoch",
        3: "Donnerstag",
        4: "Freitag",
        5: "Samstag",
        6: "Sonntag",
    }

    # target pale palette FFD6FF-FFD6E7-FFD6D6-FFEDD6-FEFFD6-DDFFD6-D8FDEF-D6FCFF-D6F1FF-D6E6FF-DCD6FF-

    # target dark palette 990040-990000-995700-969900-1a9900-08915d-008f99-006699-003b99-170099-D499FF

    COLORS = cast(
        Mapping[int, ColorDict],
        defaultdict(
            lambda: {
                "pale": "#CCCCCC",
                "dark": "",
                "normal": "#AAAAAA",
                "strong": "#000000",
            },
            [
                (
                    -1,
                    {
                        "pale": "#E1DBFF",
                        "dark": "NONE",
                        "normal": "NONE",
                        "strong": "NONE",
                    },
                ),
                (
                    0,
                    {
                        "pale": "#F5F4F6",
                        "dark": "NONE",
                        "normal": "NONE",
                        "strong": "NONE",
                    },
                ),
                (
                    1,
                    {
                        "pale": "#FFD6E7",
                        "dark": "#990040",
                        "normal": "#F862C6",
                        "strong": "#F415AA",
                    },
                ),
                (
                    5,
                    {
                        "pale": "#FFD6D6",
                        "dark": "#990000",
                        "normal": "#EF476F",
                        "strong": "#EB1E3A",
                    },
                ),
                (
                    6,
                    {
                        "pale": "#FFEDD6",
                        "dark": "#995700",
                        "normal": "#F78C6B",
                        "strong": "#F34A16",
                    },
                ),
                (
                    7,
                    {
                        "pale": "#FEFFD6",
                        "dark": "#968600",
                        "normal": "#FFD166",
                        "strong": "#FFBC1F",
                    },
                ),
                (
                    8,
                    {
                        "pale": "#DDFFD6",
                        "dark": "#1a9900",
                        "normal": "#83D483",
                        "strong": "#49C149",
                    },
                ),
                (
                    9,
                    {
                        "pale": "#D8FDEF",
                        "dark": "#08915d",
                        "normal": "#06D6A0",
                        "strong": "#06DBA2",
                    },
                ),
                (
                    10,
                    {
                        "pale": "#D6FCFF",
                        "dark": "#008f99",
                        "normal": "#0CB0A9",
                        "strong": "#1AEFE4",
                    },
                ),
                (
                    11,
                    {
                        "pale": "#D6F1FF",
                        "dark": "#006699",
                        "normal": "#29A3CC",
                        "strong": "#1FB7EA",
                    },
                ),
                (
                    12,
                    {
                        "pale": "#D6E6FF",
                        "dark": "#003b99",
                        "normal": "#1D85A8",
                        "strong": "#1082A8",
                    },
                ),
                (
                    13,
                    {
                        "pale": "#DCD6FF",
                        "dark": "#170099",
                        "normal": "#135970",
                        "strong": "#0C6583",
                    },
                ),
            ],
        ),
    )

    ALL_CLASSES = [
        "DAZ",
        "5a",
        "5b",
        "5c",
        "5d",
        "5e",
        "6a",
        "6b",
        "6c",
        "6d",
        "6e",
        "6f",
        "7a",
        "7b",
        "7c",
        "7d",
        "7e",
        "8a",
        "8b",
        "8c",
        "8d",
        "8e",
        "9a",
        "9b",
        "9c",
        "9d",
        "9e",
        "10a",
        "10b",
        "10c",
        "10d",
        "10e",
        "10f",
        "Eja",
        "Ejb",
        "Ejc",
        "Ejd",
        "Eje",
        "Q1a",
        "Q1b",
        "Q1c",
        "Q1d",
        "Q1e",
    ]


class HTMLElements:
    FOOTER_TEMPLATE = """<footer><div class="centered-box-div cbd-vertical">
<span id="letzteAenderung">Stand: {{letzteänderung}}</span><br>
<span id="letzteAktualisierung">Letzte Aktualisierung: {{letzteakt}}</span><br>
<span id="naechsteAktualisierung">Nächste Aktualisierung: {{nächsteakt}}</span>
</div><div class="centered-box-div cbd-horizontal">
<a href="/about">About</a><br>
<a href="/">Home</a>
<a href="https://samos.webuntis.com/WebUntis/monitor?school=rist2024&monitorType=subst&format=itslearning">WebUntis</a>
<a href='https://ko-fi.com/K3K71KYTMX' target='_blank'>Kaffee kaufen</a>
</div></footer>"""

    HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang="de">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Ein besserer Vertretungsplan für das Johann-Rist-Gymnasium.">
    <meta name="author" content="Mats Fangohr">
    <title>{{title}}</title>
    <link rel="canonical" href="https://vertretungsplan.fangohr.org/jrg"/>
    <link rel="icon" href="/jrg/favicon.svg" type="image/svg+xml">
    <link rel="icon" href="/favicon.ico" sizes="16x16 32x32" type="image/png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link
        href="https://fonts.googleapis.com/css2?family=Amatic+SC:wght@400;700&family=Rubik:ital,wght@0,300..900;1,300..900&display=swap"
        rel="stylesheet">
    <script defer src="https://cloud.umami.is/script.js" data-website-id="02acc140-c615-419c-b909-07dd0e7a36d7"></script>
    <style>
        .centered-box-div:last-of-type {
            margin-bottom: 4.5rem;
        }

        .centered-box-div {
            justify-content: center;
            text-align: center;
            padding: 5px;
        }

        .cbd-vertical {
        }

        .cbd-horizontal {
            display: flex;
        }

        .title-block {
            background-color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 15px;
        }

        h1 {
            text-align: center;
            margin: 0.67rem;
            font-size: 32px;
        }

        h2 {
            margin-bottom: 0;
        }

        h2:first-child {
            padding-top: 0.25rem;
            margin-top: 0;
        }

        p {
            margin-top: 3px;
        }

        a {
            text-decoration: none;
            color: {{textcolor}};
            padding-left: 0.7rem;
            padding-right: 0.7rem;
        }

        p:last-child {
            padding-bottom: 0.5rem;
            margin-bottom: 0;
        }

        hr {
            margin: 0;
            color: #666;
            background-color: #666;
            border: none;
            height: 1px;
        }

        .colorblock {
            padding-left: 12px;
            padding-right: 12px;
        }

        .daywrapper > .colorblock:last-child {
            border-radius: 0 0 15px 15px;
            padding-bottom: 12px;
        }

        .daywrapper > .colorblock:last-child > p:last-child {
            padding-bottom: 0;
        }

        .daywrapper {
            display: none;
            max-width: 800px;
            margin: 0 auto 0.5rem auto;
            padding: 5px 0 0 0;
            background-color: #FFFFFF;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            border-radius: 15px;
        }

        .daywrapper.active {
            display: block;
        }

        .navigation {
            background-color: #FFFFFF;
            width: 100%;
            bottom: -2rem;
            left: 50%;
            transform: translate(-50%, -50%);
            display: flex;
            justify-content: center;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
            height: 4rem;
        }

        .arrow {
            font-size: 2rem;
            cursor: pointer;
            margin: 0 20px;
            user-select: none;
            display: flex;
        }

        body {
            font-family: 'Rubik', sans-serif;
            color: {{textcolor}};
            background-color: #f8f8f8;
        }

        .announcement {
            display: flex;
            align-items: center;
        }

        .announce-icon, .warn-icon {
            min-width: 4rem;
            min-height: 4rem;
            width: 4rem;
            height: 4rem;
            padding: 1rem 1rem 1rem 0;
        }

        h3 {
            padding: 0.5rem 0 0 0;
            margin: 0;
        }

        main {
            margin: 8px;
        }

        svg.link-icon-svg {
            width: 1.2rem;
            height: 1.2rem;
            padding: 0 8px 0 8px;
            fill: #000;
            opacity: 40%;
        }

    </style>
    <script>
        let pageLoadDate = Date.now();
        let currentPage = {{startpage}};
        const pages = document.getElementsByClassName('daywrapper');
        document.addEventListener("DOMContentLoaded", function() {
            updateButtons();
            updateTimestamps();
            showAlerts();
        });
        document.addEventListener("load", scrollToClass);
        window.addEventListener("pageshow", () => {setTimeout(pageShow, 250)});
        window.addEventListener("hashchange", hashChanged);
        updateButtons();

        function showAlerts() {
            if (Date.now() < new Date(1763636400 * 1000).valueOf()) {
                setTimeout(() => {
                alert("Neben den Klassen sind jetzt Knöpfe - wenn ihr die drückt und euch dann den Link speichert (oder als App auf den Homebildschirm tut), scrollt die Seite beim öffnen direkt zu eurer Klasse :)\\n\\nDieser Hinweis wird noch bis Donnerstag, 12:00 angezeigt.");}, 1000)
            }
        }

        function pageShow() {
            scrollToClass();
            console.log("pageshow", event.persisted);
        }

        function hashChanged() {
            scrollToClass();
        }

        function scrollToClass() {
            let url = window.location.href;
            let hashtagPos = url.indexOf("#")
            if (hashtagPos > 0) {
                let scrollTarget = document.getElementById("klasse-" + url.substring(hashtagPos + 1));
                scrollTarget.scrollIntoView({"behavior": "smooth"});
            }
        }

        function updateButtons() {
            if (pages.length == 0) {
                return;
            }
            const leftButton = document.getElementById("leftarrow");
            const rightButton = document.getElementById("rightarrow");

            if (currentPage < pages.length - 1) {
                rightButton.style.opacity = 1;
            } else {
                rightButton.style.opacity = 0.3;
            }
            if (currentPage > 0) {
                leftButton.style.opacity = 1;
            } else {
                leftButton.style.opacity = 0.3;
            }
        }

        function showPage(index) {
            Array.from(pages).forEach((page, i) => {
                page.classList.toggle('active', i == index);
            })
        }

        function nextPage() {
            if (currentPage < pages.length - 1) {
                currentPage++;
                showPage(currentPage);
            }
            updateButtons();
            updateTimestamps();
        }

        function prevPage() {
            if (currentPage > 0) {
                currentPage--;
                showPage(currentPage);
            }
            updateButtons();
            updateTimestamps();
        }

        function getRelativeTime(date) {
            const now = new Date();
            const diffInSeconds = Math.floor((date - now) / 1000);

            const units = [
                { unit: 'year', seconds: 31536000 },
                { unit: 'month', seconds: 2592000 },
                { unit: 'day', seconds: 86400 },
                { unit: 'hour', seconds: 3600 },
                { unit: 'minute', seconds: 60 },
                { unit: 'second', seconds: 1 },
            ];

            for (const { unit, seconds } of units) {
                const delta = diffInSeconds / seconds;
                if (Math.abs(delta) >= 1 || unit === 'second') {
                const formatter = new Intl.RelativeTimeFormat('de', { numeric: 'auto' });
                return formatter.format(Math.round(delta), unit);
                }
            }
        }

        let lastUpdate = new Date({{letzteaktTimestamp}} * 1000);
        let nextUpdate = new Date({{nächsteaktTimestamp}} * 1000);

        function updateTimestamps() {
            let lastUpdateField = document.getElementById("letzteAktualisierung");
            let nextUpdateField = document.getElementById("naechsteAktualisierung");

            lastUpdateField.textContent = "Letzte Aktualisierung: " + getRelativeTime(lastUpdate);
            nextUpdateField.textContent = "Nächste Aktualisierung: " + getRelativeTime(nextUpdate);
        }

        {{reloadIfRequired}}

        setInterval(updateTimestamps, 30 * 1000);
        setTimeout(() => {setInterval(reloadIfRequired, 5 * 1000);}, 298 * 1000)
    </script>
</head>
"""

    RELOAD_IF_REQUIRED_FUNCTION = """function reloadIfRequired() {
            secondsSincePageLoad = (Date.now() - pageLoadDate) / 1000;
            secondsSinceNextUpdate = (Date.now() - nextUpdate) / 1000;
            if (secondsSincePageLoad > (60 * 5) && secondsSinceNextUpdate > 0) {
                location.reload();
            }
        }"""

    BUTTONS = f"""<div class="navigation" style="position: fixed; z-index: 100;">
    <span id="leftarrow" class="arrow" style="opacity: 0.3;" onclick="prevPage()"><svg width="2.5rem" fill="{SetupData.TEXT_COLOR}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M73.4 297.4C60.9 309.9 60.9 330.2 73.4 342.7L233.4 502.7C245.9 515.2 266.2 515.2 278.7 502.7C291.2 490.2 291.2 469.9 278.7 457.4L173.3 352L544 352C561.7 352 576 337.7 576 320C576 302.3 561.7 288 544 288L173.3 288L278.7 182.6C291.2 170.1 291.2 149.8 278.7 137.3C266.2 124.8 245.9 124.8 233.4 137.3L73.4 297.3z"/></svg></span>
    <span id="rightarrow" class="arrow" style="opacity: 1;" onclick="nextPage()"><svg width="2.5rem" fill="{SetupData.TEXT_COLOR}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M566.6 342.6C579.1 330.1 579.1 309.8 566.6 297.3L406.6 137.3C394.1 124.8 373.8 124.8 361.3 137.3C348.8 149.8 348.8 170.1 361.3 182.6L466.7 288L96 288C78.3 288 64 302.3 64 320C64 337.7 78.3 352 96 352L466.7 352L361.3 457.4C348.8 469.9 348.8 490.2 361.3 502.7C373.8 515.2 394.1 515.2 406.6 502.7L566.6 342.7z"/></svg></span></div>"""

    ABOUT_TEXT = """<footer><div class="daywrapper active">
<h1>About</h1>
<hr>
<div class="colorblock">
    <p style="font-size: 1.2rem; padding-bottom: 1rem; padding-top: 0.5rem;">
        Die Vertretungsplanseite von WebUntis ist suboptimal. Ich hoffe diese Seite ist besser - schneller, farbenfroher und (hoffentlich) angenehmer zu benutzen.<br><br>

Wenn euch irgendwas komisch vorkommt, nicht richtig funktioniert oder ihr sonstiges Feedback habt: Meldet euch gerne! Entweder direkt bei mir oder über jemanden, der weiß, wie man mich erreicht.<br><br>

Gelegentlich gibt mir WebUntis komische Daten, die zu Verarbeitungsfehlern führen - wenn etwas komisch erscheint, schaut lieber nochmal auf den offiziellen Plan (unten verlinkt) vorbei.
        <span style="float: right;">~Mats</span>
    </p>
</div></div></footer>"""

    ANNOUNCE_ICON = f"""<svg class="announce-icon" fill="{SetupData.TEXT_COLOR}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M525.2 82.9C536.7 88 544 99.4 544 112L544 528C544 540.6 536.7 552 525.2 557.1C513.7 562.2 500.4 560.3 490.9 552L444.3 511.3C400.7 473.2 345.6 451 287.9 448.3L287.9 544C287.9 561.7 273.6 576 255.9 576L223.9 576C206.2 576 191.9 561.7 191.9 544L191.9 448C121.3 448 64 390.7 64 320C64 249.3 121.3 192 192 192L276.5 192C338.3 191.8 397.9 169.3 444.4 128.7L491 88C500.4 79.7 513.9 77.8 525.3 82.9zM288 384L288 384.2C358.3 386.9 425.8 412.7 480 457.6L480 182.3C425.8 227.2 358.3 253 288 255.7L288 384z"/></svg>"""

    WARN_ICON = f"""<svg class="warn-icon" fill="{SetupData.TEXT_COLOR}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M320 64C334.7 64 348.2 72.1 355.2 85L571.2 485C577.9 497.4 577.6 512.4 570.4 524.5C563.2 536.6 550.1 544 536 544L104 544C89.9 544 76.8 536.6 69.6 524.5C62.4 512.4 62.1 497.4 68.8 485L284.8 85C291.8 72.1 305.3 64 320 64zM320 416C302.3 416 288 430.3 288 448C288 465.7 302.3 480 320 480C337.7 480 352 465.7 352 448C352 430.3 337.7 416 320 416zM320 224C301.8 224 287.3 239.5 288.6 257.7L296 361.7C296.9 374.2 307.4 384 319.9 384C332.5 384 342.9 374.3 343.8 361.7L351.2 257.7C352.5 239.5 338.1 224 319.8 224z"/></svg>"""

    LINK_ICON_DEF = """<svg style="height: 0; display: block;"><defs><path id="link-icon" d="M419.5 96c-16.6 0-32.7 4.5-46.8 12.7-15.8-16-34.2-29.4-54.5-39.5 28.2-24 64.1-37.2 101.3-37.2 86.4 0 156.5 70 156.5 156.5 0 41.5-16.5 81.3-45.8 110.6l-71.1 71.1c-29.3 29.3-69.1 45.8-110.6 45.8-86.4 0-156.5-70-156.5-156.5 0-1.5 0-3 .1-4.5 .5-17.7 15.2-31.6 32.9-31.1s31.6 15.2 31.1 32.9c0 .9 0 1.8 0 2.6 0 51.1 41.4 92.5 92.5 92.5 24.5 0 48-9.7 65.4-27.1l71.1-71.1c17.3-17.3 27.1-40.9 27.1-65.4 0-51.1-41.4-92.5-92.5-92.5zM275.2 173.3c-1.9-.8-3.8-1.9-5.5-3.1-12.6-6.5-27-10.2-42.1-10.2-24.5 0-48 9.7-65.4 27.1L91.1 258.2c-17.3 17.3-27.1 40.9-27.1 65.4 0 51.1 41.4 92.5 92.5 92.5 16.5 0 32.6-4.4 46.7-12.6 15.8 16 34.2 29.4 54.6 39.5-28.2 23.9-64 37.2-101.3 37.2-86.4 0-156.5-70-156.5-156.5 0-41.5 16.5-81.3 45.8-110.6l71.1-71.1c29.3-29.3 69.1-45.8 110.6-45.8 86.6 0 156.5 70.6 156.5 156.9 0 1.3 0 2.6 0 3.9-.4 17.7-15.1 31.6-32.8 31.2s-31.6-15.1-31.2-32.8c0-.8 0-1.5 0-2.3 0-33.7-18-63.3-44.8-79.6z"/></defs></svg>"""


class SchoolHoliday(TypedDict):
    name: str
    start: dt.date  # first date at which the message should be shown
    end: dt.date  # final date at which the message should be shown
    first_day_after: dt.date  # first day of school after the holidays


SCHOOL_HOLIDAYS: list[SchoolHoliday] = [
    {
        "name": "Herbstferien",
        "start": dt.date(2025, 10, 18),
        "end": dt.date(2025, 10, 31),
        "first_day_after": dt.date(2025, 11, 3),
    },
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
    assert holiday["end"] >= holiday["start"], "holiday must end after it begins!"
    current_date = holiday["start"]
    while current_date != holiday["end"]:
        assert current_date not in HOLIDAY_DAYS, (
            f"date {current_date} is part of two holidays!"
        )
        HOLIDAY_DAYS[current_date] = holiday
        current_date += dt.timedelta(days=1)


def is_in_holiday(date: dt.date) -> bool:
    return date in HOLIDAY_DAYS


def get_holiday(date: dt.date) -> SchoolHoliday:
    """only call if is_in_holiday(date) returns true, will return none otherwise"""
    return HOLIDAY_DAYS.get(date)  # type: ignore
