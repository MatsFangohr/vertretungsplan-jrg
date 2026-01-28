import { initializeApp } from "https://www.gstatic.com/firebasejs/12.8.0/firebase-app.js";

// https://firebase.google.com/docs/web/setup#available-libraries

const firebaseConfig = {
    apiKey: "AIzaSyCjdIkLWB21j44CP88Z1dmbhGGjVEjF7GM",
    authDomain: "vertretungsplan-ac27a.firebaseapp.com",
    projectId: "vertretungsplan-ac27a",
    storageBucket: "vertretungsplan-ac27a.firebasestorage.app",
    messagingSenderId: "500049181819",
    appId: "1:500049181819:web:2a3637c4f27571866636de"
};
const app = initializeApp(firebaseConfig);

async function subscribeToClass(classId) {
    const permission = await Notification.requestPermission();
    if (permission !== "granted") {
        alert("Benachrichtigungsrecht abgelehnt");
        return;
    }

    const token = await getToken(messaging, {
        vapidKey: "YOUR_PUBLIC_VAPID_KEY"
    });

    await fetch(
        "https://us-central1-vertretungsplan-ac27a.cloudfunctions.net/subscribeToClass",
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                token: token,
                classId: classId
            })
        }
    );

    alert("Subscribed to " + classId);
}

export async function unsubscribeFromClass(classId) {
    const token = await getToken(messaging, {
        vapidKey: VAPID_KEY
    });

    if (!token) {
        alert("No notification token found.");
        return;
    }

    await fetch(UNSUBSCRIBE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            token: token,
            classId: classId
        })
    });

    alert(`Unsubscribed from ${classId}`);
}