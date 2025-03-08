import json
import os
import time
from pathlib import Path

import streamlit as st
from pinterest_dl import PinterestDL

VERSION = "0.1.1"

MODE_OPTIONS = {
    "Board": ":material/web: Board",
    "Search": ":material/search: Search",
}
COOKIES_PATH = Path("cookies/cookies.json")
COOKIES_PATH.parent.mkdir(parents=True, exist_ok=True)


def init():
    if "use_cookies" not in st.session_state:
        st.session_state.use_cookies = False


# ui
def setup_ui():
    st.title(f"Pinterest DL {VERSION}")
    mode = st.segmented_control(
        "Mode",
        MODE_OPTIONS.values(),
        selection_mode="single",
        default=MODE_OPTIONS["Board"],
    )

    if mode == MODE_OPTIONS["Board"]:
        query = st.text_input(
            "Pinterest URL", placeholder="https://www.pinterest.com/pin/1234567890/"
        )
    else:
        query = st.text_input("Search Query", placeholder="Impressionist Art")
    project_name, image_num = project_section()
    with st.expander("Scrape Options"):
        res_x, res_y = quality_section()
        timeout = scraping_section()
        cookies_section()

    return query, project_name, res_x, res_y, image_num, timeout, mode


def cookies_section():
    col1, col2 = st.columns(2)
    with col1:
        use_cookies = st.toggle("Use Cookies", value=st.session_state.use_cookies)
    with col2:
        if use_cookies:
            st.session_state.use_cookies = True
            if st.button("Get Cookies"):
                login_dialog()
        else:
            st.session_state.use_cookies = False
    if use_cookies and not COOKIES_PATH.exists():
        st.warning(f"No cookies found under path `./{COOKIES_PATH.as_posix()}`!")


@st.dialog("Pinterest Login")
def login_dialog():
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)
    with col1:
        driver = st.selectbox("Webdriver", ["chrome", "firefox"])
    with col2:
        after_sec = st.number_input("Seconds to wait after login", 0, 60, 7, step=1)

    options = st.pills(
        "Driver Options", ["Headless", "Incognito"], selection_mode="multi", default=["Headless"]
    )
    headless = "Headless" in options
    incognito = "Incognito" in options

    if st.button("Login"):
        if not email or not password:
            st.warning("Please enter email and password!")
        else:
            with st.spinner("Logging in... (this might take a while)"):
                download_cookies(email, password, after_sec, headless, incognito, driver)
                st.rerun()


def project_section():
    col1, col2 = st.columns([2, 1])
    with col1:
        project_name = st.text_input("Project Name", placeholder="Concept Art")
    with col2:
        image_num = st.number_input("Image Limit", 1, 1000, 100, step=1)
    return project_name, image_num


def quality_section():
    col1, col2 = st.columns(2)
    with col1:
        res_x = st.number_input("Min Resolution X", 0, 4096, 0, step=64)
    with col2:
        res_y = st.number_input("Min Resolution Y", 0, 4096, 0, step=64)
    return res_x, res_y


def scraping_section():
    timeout = st.slider("Timeout (sec)", 0, 30, 10, step=1)
    return timeout


def footer():
    st.markdown(
        """
        ---
        Made with ❤️ by [Sean1832](https://github.com/Sean1832/pinterest-dl-gui)
        """
    )
    st.html(
        """<a href="https://www.buymeacoffee.com/zekezhang" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 145px !important;" ></a>"""
    )


# Logic
def download_cookies(email, password, after_sec, headless, incognito, driver):
    cookies = (
        PinterestDL.with_browser(driver, headless=headless, incognito=incognito, timeout=10)
        .login(email, password)
        .get_cookies(after_sec=after_sec)
    )
    with open(COOKIES_PATH, "w") as f:
        json.dump(cookies, f)


def scrape_images(
    url,
    project_name,
    project_dir,
    res_x,
    res_y,
    limit,
    timeout,
    msg,
):
    session_time = time.strftime("%Y%m%d%H%M%S")
    cache_path = Path("downloads", "_cache")
    cache_path.mkdir(parents=True, exist_ok=True)
    cache_filename = Path(cache_path, f"{project_name}_{session_time}.json")

    if not url or not project_name:
        msg.error("Please enter a URL and Project Name!")
        return

    if project_dir.exists():
        msg.warning("Project already exists! Merge with existing data.")

    if st.session_state.use_cookies:
        if not COOKIES_PATH.exists():
            msg.error("No cookies found!")
            return
        PinterestDL.with_api(timeout=timeout).with_cookies_path(COOKIES_PATH).scrape_and_download(
            url=url,
            output_dir=project_dir,
            limit=limit,
            min_resolution=(res_x, res_y),
            json_output=cache_filename,
        )
    else:
        PinterestDL.with_api(timeout=timeout).scrape_and_download(
            url=url,
            output_dir=project_dir,
            limit=limit,
            min_resolution=(res_x, res_y),
            json_output=cache_filename,
        )
    msg.success("Scrape Complete!")
    print("Done.")


def search_images(
    query,
    project_name,
    project_dir,
    res_x,
    res_y,
    limit,
    timeout,
    msg,
):
    session_time = time.strftime("%Y%m%d%H%M%S")
    cache_path = Path("downloads", "_cache")
    cache_path.mkdir(parents=True, exist_ok=True)
    cache_filename = Path(cache_path, f"{project_name}_{session_time}.json")

    if not query or not project_name:
        msg.error("Please enter a URL and Project Name!")
        return

    if project_dir.exists():
        msg.warning("Project already exists! Merge with existing data.")

    if st.session_state.use_cookies:
        if not COOKIES_PATH.exists():
            msg.error("No cookies found!")
            return
        PinterestDL.with_api(timeout=timeout).with_cookies_path(COOKIES_PATH).search_and_download(
            query=query,
            output_dir=project_dir,
            limit=limit,
            min_resolution=(res_x, res_y),
            json_output=cache_filename,
        )
    else:
        PinterestDL.with_api(timeout=timeout).search_and_download(
            query=query,
            output_dir=project_dir,
            limit=limit,
            min_resolution=(res_x, res_y),
            json_output=cache_filename,
        )
    msg.success("Scrape Complete!")
    print("Done.")


def main():
    st.set_page_config(page_title="Pintereset DL")
    query, project_name, res_x, res_y, threshold, timeout, mode = setup_ui()
    project_dir = Path("downloads", project_name)
    col1, col2 = st.columns([0.5, 2])
    msg = st.empty()
    with col1:
        if st.button("Scrape", type="primary"):
            with st.spinner("Scraping..."):
                if mode == MODE_OPTIONS["Board"]:
                    scrape_images(
                        query,
                        project_name,
                        project_dir,
                        res_x,
                        res_y,
                        threshold,
                        timeout,
                        msg,
                    )
                elif mode == MODE_OPTIONS["Search"]:
                    search_images(
                        query,
                        project_name,
                        project_dir,
                        res_x,
                        res_y,
                        threshold,
                        timeout,
                        msg,
                    )
                else:
                    msg.error("Invalid mode selected!")

    with col2:
        if st.button("📂 Open Directory"):
            os.startfile(project_dir)

    footer()


if __name__ == "__main__":
    init()
    main()
