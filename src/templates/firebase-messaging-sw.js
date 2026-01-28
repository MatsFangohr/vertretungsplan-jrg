import { getMessaging } from "firebase/messaging/sw";
import { onBackgroundMessage } from "firebase/messaging/sw";


firebase.initializeApp({
    // Your config from Step 1.2
    apiKey: "AIzaSyCjdIkLWB21j44CP88Z1dmbhGGjVEjF7GM",
    projectId: "vertretungsplan-ac27a",
    messagingSenderId: "500049181819",
    appId: "1:500049181819:web:2a3637c4f27571866636de"
});


const messaging = getMessaging();
messaging.onBackgroundMessage((payload) => {
    self.registration.showNotification(payload.notification.title, {
        body: payload.notification.body,
        icon: "https://vertretungsplan.fangohr.org/favicon256.png"
    });
});
