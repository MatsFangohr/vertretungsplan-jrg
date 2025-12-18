// Event Listeners

document.addEventListener("DOMContentLoaded", function () {
    updateButtons();
    updateTimestamps();
    showAlerts();
    updateLastChangeTime();
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

// Reload logic

{ { reloadIfRequired } }

setTimeout(() => { setInterval(reloadIfRequired, 5 * 1000); }, 298 * 1000)