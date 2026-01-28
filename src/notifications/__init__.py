from config import BASE_PATH
from notifications.convert import json_to_models, models_to_json, models_to_untis, untis_to_models
from notifications.send import notify_of_all_changes
from untis.types import TimetableChange


def send_notifications(changes: list[TimetableChange]) -> None:
    storage_file = BASE_PATH / "last_run_changes.json"
    if storage_file.exists():
        with storage_file.open("rb") as f:
            old_json_data = f.read()
    else:
        old_json_data = b"[]"

    old_changes = models_to_untis(json_to_models(old_json_data))

    changes_delta = [c for c in changes if c not in old_changes and c.klass.to_string() == "Q1e"]

    notify_of_all_changes(changes_delta)

    new_json_data = models_to_json(untis_to_models(changes))

    with storage_file.open("wb+") as f:
        f.write(new_json_data)
