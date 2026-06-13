import webview

from api import Api

api = Api()
window = webview.create_window("Hello world", "web/index.html", js_api=Api(), width=800, height=600)
webview.start()
