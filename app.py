import ctypes
import sys
import webview

from api import Api

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("pinterest-dl.gui")

api = Api()
window = webview.create_window(
    "Pinterest-dl",
    "web/index.html",
    js_api=api,
    width=1600,
    height=1100,
    min_size=(900, 640),
)
api.set_window(window)  # hand the bridge its handle so the run thread can push events into JS
webview.start(icon="assets/icon.ico")
