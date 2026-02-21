import datetime as dt
import subprocess
import sys
from collections.abc import Iterable

import minify_html

import config
import utils
from formatter.pages import generate_about_page, generate_index_file
from logger import info
from templates import HTML
from untis import process_raw_untis_data
from untis.data import get_holiday_data_from_date, is_in_holiday
from untis.types import WebUntisData
from untis.web import WebUntisManager
from utils import (
    get_soonest_weekday,
)


def write_out_and_copy(index_html: HTML, about_html: HTML) -> None:
    """Writes the passed strings as HTML files in the target directory specified in `config.toml`."""
    info("writing out...")
    if "--test" in sys.argv:
        main_path = config.target_dir / "test.html"
    else:
        main_path = config.target_dir / "index.html"
    about_path = config.target_dir / "about.html"

    with main_path.open("w+", encoding="utf-8") as f:
        f.write(index_html)

    with about_path.open("w+", encoding="utf-8") as f:
        f.write(about_html)

    if config.copy_command and "--debug" not in sys.argv:
        info("copying to server...")
        subprocess.run(
            config.copy_command,
            shell=True,
            check=True,
        )


def get_last_update_time(untis_data: Iterable[WebUntisData]) -> dt.datetime:
    """Returns the latest `last_update` time from passed `untis_data`."""
    return max(data.last_update for data in untis_data)


def select_dates() -> list[dt.date]:
    """Selects the dates for which the data should be fetched. If today is in a holiday, it selects
    a holiday date and the first day after the holidays. Otherwise, it selects the next 7 days up to
    a holiday.
    """
    today = utils.today()
    if is_in_holiday(today):
        tomorrow = today + dt.timedelta(days=1)
        first_day_after_holidays = get_holiday_data_from_date(today).first_day_after
        if not is_in_holiday(tomorrow):
            first_day = max(tomorrow, first_day_after_holidays)
            return [
                first_day,
                first_day + dt.timedelta(days=1),
            ]
        return [get_soonest_weekday(), first_day_after_holidays]
    else:
        candidates = [today + dt.timedelta(days=i) for i in range(7)]
        for i, date in enumerate(candidates):
            if is_in_holiday(date):
                return [*candidates[: i + 1], get_holiday_data_from_date(date).first_day_after]
        return candidates


def main() -> None:
    info(f"starting processing at {utils.now().strftime('%Y-%m-%d %H:%M:%S')}")

    raw = WebUntisManager.get_raw_untis_data(select_dates())
    untis_data = process_raw_untis_data(raw)

    last_update = get_last_update_time(untis_data.values())

    index = generate_index_file(untis_data, last_update)
    about = generate_about_page(last_update)

    minified_index = minify_html.minify(index, minify_css=True, minify_js=True)

    write_out_and_copy(minified_index, about)

    info("done!")


if __name__ == "__main__":
    main()
