from typing import Literal


def get_color(klasse: int, tone: Literal["pale", "dark", "normal", "strong"]) -> str:
    if tone not in ["pale", "dark"]:
        raise ValueError("unsupported color!")
    if tone == "pale":
        return f"var(--year-color-{klasse})"
    else:  # tone must be dark
        return f"var(--year-color-{klasse}-intense)"
