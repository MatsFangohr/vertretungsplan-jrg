from collections import defaultdict
from typing import TypedDict


class ColorDict(TypedDict):
    pale: str
    normal: str
    strong: str


COLORS: dict[int, ColorDict] = defaultdict(
    lambda: {"pale": "#FFFFFF", "normal": "#AAAAAA", "strong": "#000000"},
    [
        (0, {"pale": "#F5F4F6", "normal": None, "strong": None}),
        (1, {"pale": "#FFD6EB", "normal": "#F862C6", "strong": "#F415AA"}),
        (5, {"pale": "#FFD6D6", "normal": "#EF476F", "strong": "#EB1E3A"}),
        (6, {"pale": "#FFEDD6", "normal": "#F78C6B", "strong": "#F34A16"}),
        (7, {"pale": "#FEFFD6", "normal": "#FFD166", "strong": "#FFBC1F"}),
        (8, {"pale": "#DDFFD6", "normal": "#83D483", "strong": "#49C149"}),
        (9, {"pale": "#D8FDEF", "normal": "#06D6A0", "strong": "#06DBA2"}),
        (10, {"pale": "#D6FCFF", "normal": "#0CB0A9", "strong": "#1AEFE4"}),
        (11, {"pale": "#D6F1FF", "normal": "#29A3CC", "strong": "#1FB7EA"}),
        (12, {"pale": "#D6E6FF", "normal": "#1D85A8", "strong": "#1082A8"}),
        (13, {"pale": "#DCD6FF", "normal": "#135970", "strong": "#0C6583"}),
    ],
)

# target palette FFD6FF-FFD6E7-FFD6D6-FFEDD6-FEFFD6-DDFFD6-D8FDEF-D6FCFF-D6F1FF-D6E6FF-DCD6FF-EED6FF

# TEXT_COLOR = "#111827"

TEXT_COLOR = "#000000"

WEEKDAYS = {
    0: "Montag",
    1: "Dienstag",
    2: "Mittwoch",
    3: "Donnerstag",
    4: "Freitag",
    5: "Samstag",
    6: "Sonntag",
}

FOOTER_TEMPLATE = """<footer><div class="centered-box-div">
Letzte Änderung: {{letzteänderung}}<br>
Letzte Aktualisierung: {{letzteakt}}<br>
Nächste Aktualisierung: {{nächsteakt}}
</div><div class="centered-box-div">
<a href="/jrg/about">About</a><br>
<a href="/jrg">Home</a>
<a href="https://samos.webuntis.com/WebUntis/monitor?school=rist2024&monitorType=subst&format=itslearning">WebUntis</a>
<a href='https://ko-fi.com/K3K71KYTMX' target='_blank'>Kaffee kaufen</a>
</div></footer>"""

HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang="de">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>JRG Vertretungsplan</title>
    <link rel="canonical" href="https://vertretungsplan.fangohr.org/jrg" />
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
            display: flex;
            justify-content: center;
            text-align: center;
            padding: 5px;
        }
        
        h1 {
            text-align: center;
            margin-top: 1rem;
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
        }

        .colorblock {
            padding-left: 1rem;
            padding-right: 1rem;
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

        .announce-icon {
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

    </style>
    <script>
        let currentPage = {{startpage}};
        const pages = document.getElementsByClassName('daywrapper');
        document.addEventListener("DOMContentLoaded", function() {
            updateButtons();
        });
        updateButtons();
        
        function updateButtons() {
            const leftButton = document.getElementById("leftarrow"); 
            const rightButton = document.getElementById("rightarrow"); 
        
            if (currentPage < pages.length) {
                rightButton.style.opacity = 1;
            } else {
                rightButton.style.opacity = 0.3;
            }
            if (currentPage > 1) {
                leftButton.style.opacity = 1;
            } else {
                leftButton.style.opacity = 0.3;
            }
        }

        function showPage(index) {
            Array.from(pages).forEach((page, i) => {
                page.classList.toggle('active', i + 1 == index);
            })
        }

        function nextPage() {
            if (currentPage < pages.length) {
                currentPage++;
                showPage(currentPage);
            }
            updateButtons()
        }

        function prevPage() {
            if (currentPage > 1) {
                currentPage--;
                showPage(currentPage);
            }
            updateButtons()
        }
    </script>
</head>
"""

BUTTONS = f"""<div class="navigation" style="position: fixed;">
    <span id="leftarrow" class="arrow" style="opacity: 0.3;" onclick="prevPage()"><svg width="2.5rem" fill="{TEXT_COLOR}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M73.4 297.4C60.9 309.9 60.9 330.2 73.4 342.7L233.4 502.7C245.9 515.2 266.2 515.2 278.7 502.7C291.2 490.2 291.2 469.9 278.7 457.4L173.3 352L544 352C561.7 352 576 337.7 576 320C576 302.3 561.7 288 544 288L173.3 288L278.7 182.6C291.2 170.1 291.2 149.8 278.7 137.3C266.2 124.8 245.9 124.8 233.4 137.3L73.4 297.3z"/></svg></span>
    <span id="rightarrow" class="arrow" style="opacity: 1;" onclick="nextPage()"><svg width="2.5rem" fill="{TEXT_COLOR}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M566.6 342.6C579.1 330.1 579.1 309.8 566.6 297.3L406.6 137.3C394.1 124.8 373.8 124.8 361.3 137.3C348.8 149.8 348.8 170.1 361.3 182.6L466.7 288L96 288C78.3 288 64 302.3 64 320C64 337.7 78.3 352 96 352L466.7 352L361.3 457.4C348.8 469.9 348.8 490.2 361.3 502.7C373.8 515.2 394.1 515.2 406.6 502.7L566.6 342.7z"/></svg></span></div>"""

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
    "hideCancelWithSubstitution": False,  # ersetztes als ausgefallen anzeigen
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

ABOUT_TEXT = """<footer><div class="daywrapper active">
<h1>About</h1>
<hr>
<div class="colorblock">
    <p style="font-size: 1.2rem; padding-bottom: 1rem; padding-top: 0.5rem;">
        Die Vertretungsplanseite von WebUntis ist… na ja, sagen wir: gewöhnungsbedürftig. Das Scrollen nervt, die Farben sind etwas langweilig und bis man endlich seine Klasse findet, ist die Pause schon fast vorbei. Deshalb gibt's diese kleine Alternative - schneller, farbenfroher und (hoffentlich) angenehmer zu benutzen.<br><br>

Wenn euch irgendwas komisch vorkommt, nicht richtig funktioniert oder ihr sonstiges Feedback habt: Meldet euch gerne! Entweder direkt bei mir oder über jemanden, der weiß, wie man mich erreicht.<br><br>

Computerprogramme machen extrem selten Fehler; ich mache beim Programmieren aber durchaus mal welche. Ich kann nicht immer garantieren, dass alle Inhalte der Seite stimmen - auch wenn sie direkt von der offiziellen Seite stammen. Schaut bei Unsicherheit lieber nochmal auf den offiziellen Plan (unten verlinkt).
        <span style="float: right;">~Mats</span>
    </p>
</div></div></footer>"""

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
    "": "",
}

CRON_SPEC = "*/7 6-23 * * 0-5"

ANNOUNCE_ICON = f"""<svg class="announce-icon" fill="{TEXT_COLOR}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M525.2 82.9C536.7 88 544 99.4 544 112L544 528C544 540.6 536.7 552 525.2 557.1C513.7 562.2 500.4 560.3 490.9 552L444.3 511.3C400.7 473.2 345.6 451 287.9 448.3L287.9 544C287.9 561.7 273.6 576 255.9 576L223.9 576C206.2 576 191.9 561.7 191.9 544L191.9 448C121.3 448 64 390.7 64 320C64 249.3 121.3 192 192 192L276.5 192C338.3 191.8 397.9 169.3 444.4 128.7L491 88C500.4 79.7 513.9 77.8 525.3 82.9zM288 384L288 384.2C358.3 386.9 425.8 412.7 480 457.6L480 182.3C425.8 227.2 358.3 253 288 255.7L288 384z"/></svg>"""
