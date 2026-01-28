import datetime as dt
import itertools
from collections.abc import Iterator

from formatter.ttchange import format_ttchange
from logger import info
from untis.parsing import strip_html
from untis.types import SchoolClass, TimetableChange
from utils import get_weekday_str

from .firebase import messaging


def send_notification(klass: str, title: str, body: str) -> None:
    message = messaging.Message(
        data={
            "title": title,
            "body": body,
            "class": klass,
            "image": "https://vertretungsplan.fangohr.org/favicon256.png",
        },
        topic=f"class-{klass}",
    )

    info(f"sending message to {klass}")
    messaging.send(message)


def notify_of_ttchange(
    klass: SchoolClass, date: dt.date, newchanges: Iterator[TimetableChange]
) -> None:
    weekday = get_weekday_str(date)
    klass_str = klass.to_string()
    send_notification(
        klass_str,
        f"{klass_str}: Neue Änderung am {weekday}",
        "\n".join(
            map(
                strip_html,
                map(format_ttchange, newchanges),
            ),
        ),
    )


def notify_of_all_changes(newchanges: list[TimetableChange]) -> None:
    for (klass, date), changes in itertools.groupby(newchanges, lambda x: (x.klass, x.date)):
        notify_of_ttchange(klass, date, changes)
