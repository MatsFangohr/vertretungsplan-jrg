import pathlib
import tomllib

from content import BASE_PATH

with open(BASE_PATH / "config.toml", "rb") as f:
    configdata = tomllib.load(f)

copy_command: str = configdata["copy-to-server-command"]
target_dir: pathlib.Path = pathlib.Path(configdata["target-dir"])
