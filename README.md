# Pinterest Downloader GUI


<a href="https://www.buymeacoffee.com/zekezhang" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 145px !important;" ></a>

This is a web GUI for scraping Pinterest images with a given URL. It is built on top of the [pinterest-dl](https://github.com/sean1832/pinterest-dl) api, which is a Python package and command line tool for downloading Pinterest images.

> [!WARNING] DISCLAIMER
> This project is independent and not affiliated with Pinterest. It's designed solely for educational purposes. Please be aware that automating the scraping of websites might conflict with their [Terms of Service](https://developers.pinterest.com/terms/). The repository owner disclaims any liability for misuse of this tool. Use it responsibly and at your own legal risk.

## Installation
#### Automatic Installation
1. Clone the repository
```bash
git clone https//github.com/sean1832/pinterest-dl-gui.git
```
2. Execute `gui.bat` to start the server

#### Manual Installation
Some user might need to install manually.
1. Clone the repository
```bash
git clone https//github.com/sean1832/pinterest-dl-gui.git
```
2. Create a virtual environment and activate (optional but recommended)
```bash
python -m venv venv
./venv/Scripts/activate
```

3. Install the required packages
```bash
pip install -r requirements.txt
```

4. Start the server
```bash
streamlit run gui.py
```

> [!TIP]
> Subsequent runs after installation can be done by executing `gui.bat` even if you installed manually.

## Grafical User Interface
![alt text](image.png)
