import webview

from api import Api

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
webview.start()
