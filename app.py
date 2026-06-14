import ctypes
import sys
import webview
from pathlib import Path

from api import Api


def _base_dir() -> Path:
    # Nuitka injects __nuitka_binary_dir at compile time; it points to the directory
    # where bundled data files live (temp extraction dir for --onefile, dist dir for
    # --standalone). Falls back to the source file's directory in dev mode.
    try:
        return Path(__nuitka_binary_dir)  # type: ignore[name-defined]  # noqa: F821
    except NameError:
        return Path(__file__).parent


_base = _base_dir()

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("pinterest-dl.gui")

api = Api()
window = webview.create_window(
    "Pinterest-dl",
    str(_base / "web" / "index.html"),
    js_api=api,
    width=1600,
    height=1100,
    min_size=(900, 640),
)
api.set_window(window)  # hand the bridge its handle so the run thread can push events into JS
webview.start(icon=str(_base / "assets" / "icon.ico"))
