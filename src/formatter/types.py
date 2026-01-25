from typing import TypedDict

type HTML = str


class HTMLFiles(TypedDict):
    main: HTML
    about: HTML


class ColorDict(TypedDict):
    pale: str
    dark: str
    normal: str
    strong: str
