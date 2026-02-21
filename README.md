# vertretungsplan-jrg
A formatter to display substitution data from Untis.

When run, it will
- automatically fetch data from the Untis API,
- format it as a web page and
- write the result to a fully self-contained HTML file.

If the demo is running, you can see a dummy output [here](https://vertretungsplan.fangohr.org).

## Configuration
Make a copy of `example-config.toml` and rename it to `config.toml`. Adjust the parameters as you wish according to the comments provided.

## Setup
To run this project yourself:
1. [Install `uv`](https://docs.astral.sh/uv/getting-started/installation) via `cargo`/`winget`/`pip` or run the standalone installer.
2. Clone the repository (or download the ZIP if you must).
3. Copy or rename `example-config.toml` as `config.toml` and adjust the config as required.
4. Run `uv run src/main.py`.

That's it! `uv` will handle dependencies on its own and run the project when it's ready.

## License
This project is licensed under the MIT license.
