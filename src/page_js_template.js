// Event Listeners

document.addEventListener("DOMContentLoaded", function () {
    updateButtons();
    updateTimestamps();
    showAlerts();
    updateLastChangeTime();
    changeTextColors();
});

document.addEventListener("load", scrollToClass);

window.addEventListener("pageshow", () => { setTimeout(scrollToClass, 250) });

window.addEventListener("hashchange", scrollToClass);

// Setup

let currentPage = {{ startpage }};
const pages = document.getElementsByClassName('daywrapper');
updateButtons();

// Alerts

function showAlerts() {
    ; // no alerts currently
}

// Time information

const lastChange = new Date({{ letzteänderungTimestamp }} * 1000);
const lastUpdate = new Date({{ letzteaktTimestamp }} * 1000);
const nextUpdate = new Date({{ nächsteaktTimestamp }} * 1000);

function updateLastChangeTime() {
    const lastChangeFields = document.querySelectorAll(".letzte-aenderung");

    lastChangeFields.forEach(el => {
        el.textContent = "Letzte Änderung: " + getRelativeTime(lastChange);
    });
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


setInterval(updateTimestamps, 30 * 1000);

function updateTimestamps() {
    const lastUpdateFields = document.querySelectorAll(".letzte-aktualisierung");
    const nextUpdateFields = document.querySelectorAll(".naechste-aktualisierung");

    lastUpdateFields.forEach(el => {
        el.textContent = "Letzte Akt.: " + getRelativeTime(lastUpdate);
    });

    nextUpdateFields.forEach(el => {
        el.textContent = "Nächste Akt.: " + getRelativeTime(nextUpdate);
    });
}

// Page logic

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

// Scrolling

function scrollToClass() {
    let url = window.location.href;
    let hashtagPos = url.indexOf("#")
    if (hashtagPos > 0) {
        let scrollTarget = document.getElementById("klasse-" + url.substring(hashtagPos + 1));
        scrollTarget.scrollIntoView({ "behavior": "smooth" });
    }
}

// Color changes

function interpolateColors(c1, c2, ratio) {
    const r1 = parseInt(c1.substring(1, 3), 16);
    const g1 = parseInt(c1.substring(3, 5), 16);
    const b1 = parseInt(c1.substring(5, 7), 16);

    const r2 = parseInt(c2.substring(1, 3), 16);
    const g2 = parseInt(c2.substring(3, 5), 16);
    const b2 = parseInt(c2.substring(5, 7), 16);

    const r = Math.round(r1 + (r2 - r1) * ratio);
    const g = Math.round(g1 + (g2 - g1) * ratio);
    const b = Math.round(b1 + (b2 - b1) * ratio);

    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

function changeTextColorsSingle(tolerance, duration, targetTime, cssClass, targetColor) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - targetTime) / 1000);
    if (diffInSeconds > tolerance) {
        const ratio = Math.min(1, (diffInSeconds - tolerance) / duration);
        const newColor = interpolateColors("#000000", targetColor, ratio);

        const fieldsToChange = document.querySelectorAll("." + cssClass);
        fieldsToChange.forEach(el => {
            el.style.color = newColor;
        });
    }
}

setInterval(changeTextColors, 30 * 1000);

function changeTextColors() {
    // seconds after which red begins
    const updateTolerance = 5 * 60;
    const lastChangeTolerance = 48 * 60 * 60;
    // seconds after which red is max
    const updateToleranceDuration = 10 * 60;
    const lastChangeToleranceDuration = 48 * 60 * 60;


    changeTextColorsSingle(updateTolerance, updateToleranceDuration, lastUpdate, "naechste-aktualisierung", "#ff0000")
    changeTextColorsSingle(lastChangeTolerance, lastChangeToleranceDuration, lastChange, "letzte-aenderung", "#ff0000")
}

// Reload logic

// {{ reloadIfRequired }}

setTimeout(() => { setInterval(reloadIfRequired, 5 * 1000); }, 298 * 1000)