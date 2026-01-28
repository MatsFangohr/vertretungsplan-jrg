importScripts("https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js");

firebase.initializeApp({
    apiKey: "AIzaSyCjdIkLWB21j44CP88Z1dmbhGGjVEjF7GM",
    projectId: "vertretungsplan-ac27a",
    messagingSenderId: "500049181819",
    appId: "1:500049181819:web:2a3637c4f27571866636de"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function (payload) {
    const title = payload.data.title;
    const body = payload.data.body;
    const icon = payload.data.image
    const url = "https://vertretungsplan.fangohr.org#" + payload.data.class;

    self.registration.showNotification(title, {
        body: body,
        icon: icon,
        data: { url: url }
    });
});

messaging.onMessage((payload) => {
    alert("Neue Informationen für deine Klasse sind verfügbar! Bitte lade die Seite einmal neu.")
})

self.addEventListener("notificationclick", function (event) {
    event.notification.close();
    const url = event.notification.data.url;
    event.waitUntil(clients.openWindow(url));
});