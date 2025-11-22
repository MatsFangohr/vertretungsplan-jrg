import logging
import time
from collections.abc import Callable

start_time = time.time()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def general_log(message: str, func: Callable[[str], None]) -> None:
    current_time = time.time()
    elapsed = current_time - start_time
    func(f"[{elapsed:05.3f}s] {message}")


def warn(message: str) -> None:
    general_log(message, logger.warning)


def info(message: str) -> None:
    general_log(message, logger.info)
