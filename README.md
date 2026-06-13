# Pinterest Downloader GUI


<a href="https://www.buymeacoffee.com/zekezhang" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 145px !important;" ></a>

This is a web GUI for scraping Pinterest images with a given URL. It is built on top of the [pinterest-dl](https://github.com/sean1832/pinterest-dl) api, which is a Python package and command line tool for downloading Pinterest images.

> [!WARNING]
> This project is independent and not affiliated with Pinterest. It's designed solely for educational purposes. Please be aware that automating the scraping of websites might conflict with their [Terms of Service](https://developers.pinterest.com/terms/). The repository owner disclaims any liability for misuse of this tool. Use it responsibly and at your own legal risk.


## Install from source
1. Clone the repository
```bash
git clone https://github.com/sean1832/pinterest-dl-gui.git
cd pinterest-dl-gui
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Build the frontend
```bash
python build.py
```

4. Run the app
```bash
python app.py
```

## Architecture
This project is built with a Python backend using pywebview to create a desktop application, and a Svelte frontend for the user interface.

The project structure is organized as follows:

```
pinterest_gui/
 ├─ app.py                  # pywebview entry point
 ├─ api.py                  # methods exposed to Svelte
 ├─ core/
 │   ├─ downloader.py       # scrape/search logic
 │   ├─ cookies.py          # cookie login/save/load
 │   ├─ ffmpeg.py           # ffmpeg detection
 │   ├─ paths.py            # download/cache paths
 │   └─ platform.py         # open folder
 └─ frontend/
     └─ Svelte app
```
The Python main process starts the pywebview window, exposes a Python API to the Svelte frontend, 
calls the pinterest_dl functions, manages cookies/downloads/cache, and handles opening folders and checking for ffmpeg.