from typing import TypedDict


class RawAnnouncementData(TypedDict):
    subject: str
    body: str


class RawAnnouncementsData(TypedDict):
    messages: list[RawAnnouncementData]


class RawTTChange(TypedDict):
    data: tuple[str, str, str, str, str]
    group: str
    cellClasses: dict[str, str]


class RawWebUntisData(TypedDict):
    date: str
    rows: list[RawTTChange]
    messageData: RawAnnouncementsData
    weekDay: str
    lastUpdate: str
