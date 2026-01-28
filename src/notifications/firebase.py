import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging as messaging  # noqa: PLC0414

from config import BASE_PATH
from logger import info

info("signing in to firebase...")
cred = credentials.Certificate(BASE_PATH / "firebaseAdminPk.json")
firebase_admin.initialize_app(cred)
info("firebase login complete.")
