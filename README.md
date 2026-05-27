### vial-gui

# Docs and getting started

### Please visit [get.vial.today](https://get.vial.today/) to get started with Vial

Vial is an open-source cross-platform (Windows, Linux and Mac) GUI and a QMK fork for configuring your keyboard in real time.


![](https://get.vial.today/img/vial-win-1.png)


---


#### Releases

Visit https://get.vial.today/ to download a binary release of Vial.

#### Development

Requires Python 3.13 or newer. The project uses [uv](https://docs.astral.sh/uv/) to manage dependencies and Python versions; it will install a matching Python automatically.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (`brew install uv`, `pipx install uv`, or the install script).

Install dependencies (creates `.venv/`):

```
uv sync
```

To launch the application:

```
uv run python src/main/python/main.py
```

To produce a frozen build with PyInstaller (platform-specific):

```
uv sync --extra build
uv run pyinstaller vial-mac.spec     # macOS  -> dist/Vial.app
uv run pyinstaller vial-win.spec     # Windows -> dist/Vial/Vial.exe
uv run pyinstaller vial-linux.spec   # Linux   -> dist/Vial/Vial
```

If you'd rather use plain pip:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` lists the same direct dependencies; `uv.lock` additionally pins exact transitive versions for reproducible builds.
