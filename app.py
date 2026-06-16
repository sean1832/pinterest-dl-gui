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

    # The windowed build has no console, so each ffmpeg child (spawned by pinterest_dl
    # to remux videos) opens its own console window -- visible as flashing cmd windows,
    # one per download worker. Default child processes to CREATE_NO_WINDOW so they stay
    # hidden; callers that set their own creationflags are left untouched.
    import subprocess

    _orig_popen_init = subprocess.Popen.__init__

    def _no_window_popen_init(self, *args, **kwargs):
        if kwargs.get("creationflags", 0) == 0:
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        _orig_popen_init(self, *args, **kwargs)

    subprocess.Popen.__init__ = _no_window_popen_init

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
