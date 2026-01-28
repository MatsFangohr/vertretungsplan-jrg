/**
 * Import function triggers from their respective submodules:
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

const { setGlobalOptions } = require("firebase-functions");
const logger = require("firebase-functions/logger");

setGlobalOptions({ maxInstances: 10 });

const functions = require("firebase-functions");
const admin = require("firebase-admin");
const cors = require("cors")({ origin: "https://vertretungsplan.fangohr.org" });

admin.initializeApp();

exports.subscribeToClass = functions.https.onRequest((req, res) => {
    cors(req, res, async () => {
        if (req.method !== "POST") {
            return res.status(405).send("Method Not Allowed");
        }

        const { token, classId } = req.body;

        if (!token || !classId) {
            return res.status(400).json({ error: "Missing token or classId" });
        }

        try {
            await admin.messaging().subscribeToTopic(
                token,
                `class-${classId}`
            );

            res.json({ status: "subscribed", classId });
        } catch (err) {
            console.error(err);
            res.status(500).json({ error: "Subscription failed" });
        }
    })
});

exports.unsubscribeFromClass = functions.https.onRequest((req, res) => {
    cors(req, res, async () => {
        const { token, classId } = req.body;

        await admin.messaging().unsubscribeFromTopic(
            token,
            `class-${classId}`
        );

        res.json({ status: "unsubscribed" });
    })
});
