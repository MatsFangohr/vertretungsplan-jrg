import pathlib
import tomllib

from content import BASE_PATH

config_path = BASE_PATH / "config.toml"
with config_path.open("rb") as f:
    configdata = tomllib.load(f)

copy_command: str = configdata["copy-to-server-command"]
target_dir: pathlib.Path = pathlib.Path(configdata["target-dir"])
