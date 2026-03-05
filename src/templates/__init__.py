"""Contains various HTML, CSS and JS templates used for generating the page. Doesn't contain any
logic.
"""

# ruff: noqa: E501
import config
from config import BASE_PATH

type HTML = str


def load_js() -> str:
    path = BASE_PATH / "src" / "templates" / "page_js_template.js"
    with path.open(encoding="utf-8") as f:
        return f.read()


def load_css() -> str:
    path = BASE_PATH / "src" / "templates" / "page_css.css"
    with path.open(encoding="utf-8") as f:
        return f.read()


FOOTER_TEMPLATE: HTML = f"""<footer><div class="centered-box-div" style="padding-top: 0;">
<span id="gitInfo">running {{{{gitHash}}}}</span>
</div>
<div class="centered-box-div cbd-flex">
<a href="/about">About</a>
<a href="/">Home</a>
<a href="{config.untis_url}">WebUntis</a>
</div></footer>"""

HEAD_TEMPLATE: HTML = (
    """<!DOCTYPE html>
<html lang="de">

<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="description" content="Ein besserer Vertretungsplan für das Johann-Rist-Gymnasium.">
<meta name="author" content="Mats Fangohr">
<title>{{title}}</title>
<link rel="canonical" href="https://vertretungsplan.fangohr.org"/>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="16x16 32x32" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rubik:ital,wght@0,300..900;1,300..900&display=swap" rel="stylesheet">
<script defer src="https://cloud.umami.is/script.js" data-website-id="02acc140-c615-419c-b909-07dd0e7a36d7"></script>
<style>"""
    + load_css()
    + """</style>
<script>"""
    + load_js().replace("{{ ", "{{").replace(" }}", "}}")
    + """</script>
</head>
"""
)

ERROR_MESSAGE: HTML = f"""Es kann sein, dass manche Einträge fehlen. Schaut sicherheitshalber bei <a style="color: unset; padding: unset;" href="{config.untis_url}">WebUntis</a> nach. Schreibt mir gerne, dann ist der Fehler bald weg. Wahrscheinlich hat WebUntis wieder das Format geändert."""

RELOAD_IF_REQUIRED_FUNCTION: HTML = """
const pageLoadDate = new Date();
function reloadIfRequired() {
        secondsSincePageLoad = (Date.now() - pageLoadDate) / 1000;
        secondsSinceNextUpdate = (Date.now() - nextUpdate) / 1000;
        if (secondsSincePageLoad > (60 * 5) && secondsSinceNextUpdate > 0) {
            location.reload();
        }
    }"""

THEME_SWITCH_BUTTON = """<label class="theme-toggle" style="margin: auto 0.5rem auto auto">
<input type="checkbox" id="theme-toggle"/>
<span class="theme-toggle-sr">Toggle theme</span>
<svg
xmlns="http://www.w3.org/2000/svg"
class="theme-toggle-inner"
viewBox="0 0 32 32"
fill="var(--theme-toggle-color)"
>
<clipPath id="theme-toggle-inner__clip">
    <path d="M0 0h32v32h-32ZM6 16A1 1 0 0026 16 1 1 0 006 16" />
</clipPath>
<g clip-path="url(#theme-toggle-inner__clip)">
    <path d="M30.7 21.3 27.1 16l3.7-5.3c.4-.5.1-1.3-.6-1.4l-6.3-1.1-1.1-6.3c-.1-.6-.8-.9-1.4-.6L16 5l-5.4-3.7c-.5-.4-1.3-.1-1.4.6l-1 6.3-6.4 1.1c-.6.1-.9.9-.6 1.3L4.9 16l-3.7 5.3c-.4.5-.1 1.3.6 1.4l6.3 1.1 1.1 6.3c.1.6.8.9 1.4.6l5.3-3.7 5.3 3.7c.5.4 1.3.1 1.4-.6l1.1-6.3 6.3-1.1c.8-.1 1.1-.8.7-1.4zM16 25.1c-5.1 0-9.1-4.1-9.1-9.1 0-5.1 4.1-9.1 9.1-9.1s9.1 4.1 9.1 9.1c0 5.1-4 9.1-9.1 9.1z" />
</g>
<path
    class="theme-toggle-inner-circle"
    d="M16 7.7c-4.6 0-8.2 3.7-8.2 8.2s3.6 8.4 8.2 8.4 8.2-3.7 8.2-8.2-3.6-8.4-8.2-8.4zm0 14.4c-3.4 0-6.1-2.9-6.1-6.2s2.7-6.1 6.1-6.1c3.4 0 6.1 2.9 6.1 6.2s-2.7 6.1-6.1 6.1z"
/>
<path
    class="theme-toggle-inner__inner"
    d="M16 9.5c-3.6 0-6.4 2.9-6.4 6.4s2.8 6.5 6.4 6.5 6.4-2.9 6.4-6.4-2.8-6.5-6.4-6.5z"
/>
</svg>
</label>"""

NAVIGATION: HTML = """
<div class="navigation" style="position: fixed; z-index: 100;">
    <span id="leftarrow" class="arrow" style="opacity: 0.3;" onclick="prevPage()"><svg width="2.5rem" fill="var(--text-color)" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M73.4 297.4C60.9 309.9 60.9 330.2 73.4 342.7L233.4 502.7C245.9 515.2 266.2 515.2 278.7 502.7C291.2 490.2 291.2 469.9 278.7 457.4L173.3 352L544 352C561.7 352 576 337.7 576 320C576 302.3 561.7 288 544 288L173.3 288L278.7 182.6C291.2 170.1 291.2 149.8 278.7 137.3C266.2 124.8 245.9 124.8 233.4 137.3L73.4 297.3z"/></svg></span>
    <span id="rightarrow" class="arrow" style="opacity: 1;" onclick="nextPage()"><svg width="2.5rem" fill="var(--text-color)" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M566.6 342.6C579.1 330.1 579.1 309.8 566.6 297.3L406.6 137.3C394.1 124.8 373.8 124.8 361.3 137.3C348.8 149.8 348.8 170.1 361.3 182.6L466.7 288L96 288C78.3 288 64 302.3 64 320C64 337.7 78.3 352 96 352L466.7 352L361.3 457.4C348.8 469.9 348.8 490.2 361.3 502.7C373.8 515.2 394.1 515.2 406.6 502.7L566.6 342.7z"/></svg></span>
</div>"""

ABOUT_TEXT: HTML = """
<div class="daywrapper active">
    <h1>About</h1>
    <hr>
    <div class="colorblock">
        <p style="font-size: 1.2rem; padding-bottom: 1rem; padding-top: 0.5rem;">
        Die Vertretungsplanseite von WebUntis ist suboptimal. Ich hoffe diese Seite ist besser - schneller, farbenfroher und (hoffentlich) angenehmer zu benutzen.<br><br>

        Wenn euch irgendwas komisch vorkommt, nicht richtig funktioniert oder ihr sonstiges Feedback habt: Meldet euch gerne! Entweder bei mir persönlich, über einen Kontakt oder unter <a href="mailto:vertretungsplan@fangohr.org" class="bluelink">vertretungsplan@fangohr.org</a>.<br><br>

        Gelegentlich gibt mir WebUntis komische Daten, die zu Verarbeitungsfehlern führen - wenn etwas komisch erscheint, schaut lieber nochmal auf den offiziellen Plan (unten verlinkt).
        <span style="float: right;">~Mats</span>
        </p>
    </div>
</div>"""

ANNOUNCE_ICON: HTML = """<svg class="announce-icon" fill="var(--text-color)" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M525.2 82.9C536.7 88 544 99.4 544 112L544 528C544 540.6 536.7 552 525.2 557.1C513.7 562.2 500.4 560.3 490.9 552L444.3 511.3C400.7 473.2 345.6 451 287.9 448.3L287.9 544C287.9 561.7 273.6 576 255.9 576L223.9 576C206.2 576 191.9 561.7 191.9 544L191.9 448C121.3 448 64 390.7 64 320C64 249.3 121.3 192 192 192L276.5 192C338.3 191.8 397.9 169.3 444.4 128.7L491 88C500.4 79.7 513.9 77.8 525.3 82.9zM288 384L288 384.2C358.3 386.9 425.8 412.7 480 457.6L480 182.3C425.8 227.2 358.3 253 288 255.7L288 384z"/></svg>"""

WARN_ICON: HTML = """<svg class="warn-icon" fill="var(--text-color)" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M320 64C334.7 64 348.2 72.1 355.2 85L571.2 485C577.9 497.4 577.6 512.4 570.4 524.5C563.2 536.6 550.1 544 536 544L104 544C89.9 544 76.8 536.6 69.6 524.5C62.4 512.4 62.1 497.4 68.8 485L284.8 85C291.8 72.1 305.3 64 320 64zM320 416C302.3 416 288 430.3 288 448C288 465.7 302.3 480 320 480C337.7 480 352 465.7 352 448C352 430.3 337.7 416 320 416zM320 224C301.8 224 287.3 239.5 288.6 257.7L296 361.7C296.9 374.2 307.4 384 319.9 384C332.5 384 342.9 374.3 343.8 361.7L351.2 257.7C352.5 239.5 338.1 224 319.8 224z"/></svg>"""

LINK_ICON_DEF: HTML = """<svg style="height: 0; display: block;"><defs><path id="link-icon" d="M419.5 96c-16.6 0-32.7 4.5-46.8 12.7-15.8-16-34.2-29.4-54.5-39.5 28.2-24 64.1-37.2 101.3-37.2 86.4 0 156.5 70 156.5 156.5 0 41.5-16.5 81.3-45.8 110.6l-71.1 71.1c-29.3 29.3-69.1 45.8-110.6 45.8-86.4 0-156.5-70-156.5-156.5 0-1.5 0-3 .1-4.5 .5-17.7 15.2-31.6 32.9-31.1s31.6 15.2 31.1 32.9c0 .9 0 1.8 0 2.6 0 51.1 41.4 92.5 92.5 92.5 24.5 0 48-9.7 65.4-27.1l71.1-71.1c17.3-17.3 27.1-40.9 27.1-65.4 0-51.1-41.4-92.5-92.5-92.5zM275.2 173.3c-1.9-.8-3.8-1.9-5.5-3.1-12.6-6.5-27-10.2-42.1-10.2-24.5 0-48 9.7-65.4 27.1L91.1 258.2c-17.3 17.3-27.1 40.9-27.1 65.4 0 51.1 41.4 92.5 92.5 92.5 16.5 0 32.6-4.4 46.7-12.6 15.8 16 34.2 29.4 54.6 39.5-28.2 23.9-64 37.2-101.3 37.2-86.4 0-156.5-70-156.5-156.5 0-41.5 16.5-81.3 45.8-110.6l71.1-71.1c29.3-29.3 69.1-45.8 110.6-45.8 86.6 0 156.5 70.6 156.5 156.9 0 1.3 0 2.6 0 3.9-.4 17.7-15.1 31.6-32.8 31.2s-31.6-15.1-31.2-32.8c0-.8 0-1.5 0-2.3 0-33.7-18-63.3-44.8-79.6z"/></defs></svg>"""
