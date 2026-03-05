import pathlib
import tomllib

BASE_PATH = pathlib.Path(__file__).parent.parent.resolve()


config_path = BASE_PATH / "config.toml"
with config_path.open("rb") as f:
    configdata = tomllib.load(f)

copy_command: str = configdata["copy-to-server-command"]
target_dir: pathlib.Path = pathlib.Path(configdata["target-dir"])
cron_specs: list[str] = configdata["cron-specs"]
untis_url: str = configdata["untis-url"]
api_url: str = configdata["untis-api-url"]
