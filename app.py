import webview

from api import Api

api = Api()
window = webview.create_window(
    "Pinterest-dl",
    "web/index.html",
    js_api=api,
    width=1280,
    height=860,
    min_size=(900, 640),
)
webview.start()
