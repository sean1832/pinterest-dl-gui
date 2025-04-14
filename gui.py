import json
import os
import time
from pathlib import Path

import streamlit as st
from pinterest_dl import PinterestDL

# ========================== Configuration Section ==========================
VERSION = "0.2.0"
MODE_OPTIONS = {
    "Board": ":material/web: Board",
    "Search": ":material/search: Search",
}
COOKIES_PATH = Path("cookies/cookies.json")
COOKIES_PATH.parent.mkdir(parents=True, exist_ok=True)


# ========================== UI Functions Section ==========================
def init_state():
    """Initialize Streamlit session state variables."""
    if "use_cookies" not in st.session_state:
        st.session_state.use_cookies = False
    if "remove_no_cap" not in st.session_state:
        st.session_state.remove_no_cap = False


def setup_ui():
    """Set up main UI components and return user inputs."""
    st.title(f"Pinterest DL {VERSION}")
    mode = st.segmented_control(
        "Mode",
        list(MODE_OPTIONS.values()),
        selection_mode="single",
        default=MODE_OPTIONS["Board"],
    )

    # Query input depends on selected mode.
    if mode == MODE_OPTIONS["Board"]:
        query = st.text_input(
            "Pinterest URL", placeholder="https://www.pinterest.com/pin/1234567890/"
        )
    else:
        query = st.text_input("Search Query", placeholder="Impressionist Art")

    # Gather project information.
    project_name, image_limit = project_section()
    with st.expander("Scrape Options"):
        res_x, res_y = quality_section()
        timeout, delay = scraping_section()
        caption_type = caption_selection()
        cookies_section()

    return query, project_name, res_x, res_y, image_limit, timeout, delay, mode, caption_type


def cookies_section():
    """UI for cookie usage toggle and button for login dialog."""
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


def caption_selection():
    """UI for selecting caption options."""
    caption_type = st.selectbox(
        "Caption Type",
        ["none", "txt", "json", "metadata"],
        index=0,
    )
    remove_no_cap = st.toggle(
        "Remove No Caption",
        value=False,
        help="Remove images without captions from the final output. (Set `Caption Type` other than `none` to enable)",
        disabled=(caption_type == "none"),
    )
    st.session_state.remove_no_cap = remove_no_cap
    return caption_type


@st.dialog("Pinterest Login")
def login_dialog():
    """Dialog box for logging in and retrieving cookies."""
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
    """UI for specifying the project name and image limit."""
    col1, col2 = st.columns([2, 1])
    with col1:
        project_name = st.text_input("Project Name", placeholder="Concept Art")
    with col2:
        image_limit = st.number_input("Image Limit", 1, 1000, 100, step=1)
    return project_name, image_limit


def quality_section():
    """UI for choosing minimum image resolution."""
    col1, col2 = st.columns(2)
    with col1:
        res_x = st.number_input("Min Resolution X", 0, 4096, 0, step=64)
    with col2:
        res_y = st.number_input("Min Resolution Y", 0, 4096, 0, step=64)
    return res_x, res_y


def scraping_section() -> tuple[float, float]:
    """UI for setting timeout and delay options."""
    timeout = st.slider("Timeout (sec)", 0.0, 30.0, 10.0, help="Timeout for each request")
    delay = st.slider("Delay (sec)", 0.0, 2.0, 0.8, help="Delay between requests")
    return timeout, delay


def footer():
    """Custom footer displayed on the page."""
    bg_color = "#262730"
    txt_color = "#FFF"
    border_color = "#444"
    custom_css = f"""
    <style>
        footer {{ visibility: hidden; }}
        .stApp {{ margin-bottom: 60px; }}
        .custom-footer {{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: {bg_color};
            color: {txt_color};
            text-align: center;
            padding: 10px;
            font-size: 12px;
            border-top: 1px solid {border_color};
            z-index: 100;
        }}
        .custom-footer a {{
            color: {txt_color};
            text-decoration: none;
        }}
        .custom-footer a:hover {{
            text-decoration: underline;
        }}
    </style>
    """
    custom_footer = """
    <div class="custom-footer">
        Made with ❤️ by <a href="https://github.com/Sean1832/pinterest-dl-gui" target="_blank">Sean1832</a>
        | <a href="https://www.buymeacoffee.com/zekezhang" target="_blank">Buy me a coffee</a>
    </div>
    """
    st.markdown(custom_css + custom_footer, unsafe_allow_html=True)


# ========================== Scraper Functions Section ==========================
def download_cookies(email, password, after_sec, headless, incognito, driver):
    """Perform login and save cookies."""
    cookies = (
        PinterestDL.with_browser(driver, headless=headless, incognito=incognito, timeout=10)
        .login(email, password)
        .get_cookies(after_sec=after_sec)
    )
    with open(COOKIES_PATH, "w") as f:
        json.dump(cookies, f)


def scrape_images(
    url, project_name, project_dir, res_x, res_y, limit, timeout, delay, caption, msg
):
    """Scrape images from a Pinterest board URL."""
    session_time = time.strftime("%Y%m%d%H%M%S")
    cache_path = Path("downloads", "_cache")
    cache_path.mkdir(parents=True, exist_ok=True)
    cache_filename = Path(cache_path, f"{project_name}_{session_time}.json")

    if not url or not project_name:
        msg.error("Please enter a URL and Project Name!")
        return

    if project_dir.exists():
        msg.warning("Project already exists! Merge with existing data.")

    api_instance = PinterestDL.with_api(timeout=timeout)
    if st.session_state.use_cookies:
        if not COOKIES_PATH.exists():
            msg.error("No cookies found!")
            return
        api_instance = api_instance.with_cookies_path(COOKIES_PATH)

    api_instance.scrape_and_download(
        url=url,
        output_dir=project_dir,
        num=limit,
        min_resolution=(res_x, res_y),
        cache_path=cache_filename,
        delay=delay,
        remove_no_alt=st.session_state.remove_no_cap,
        caption=caption,
    )
    msg.success("Scrape Complete!")
    print("Done.")


def search_images(
    query, project_name, project_dir, res_x, res_y, limit, timeout, delay, caption, msg
):
    """Search for images using a query and download results."""
    session_time = time.strftime("%Y%m%d%H%M%S")
    cache_path = Path("downloads", "_cache")
    cache_path.mkdir(parents=True, exist_ok=True)
    cache_filename = Path(cache_path, f"{project_name}_{session_time}.json")

    if not query or not project_name:
        msg.error("Please enter a query and Project Name!")
        return

    if project_dir.exists():
        msg.warning("Project already exists! Merge with existing data.")

    api_instance = PinterestDL.with_api(timeout=timeout)
    if st.session_state.use_cookies:
        if not COOKIES_PATH.exists():
            msg.error("No cookies found!")
            return
        api_instance = api_instance.with_cookies_path(COOKIES_PATH)

    api_instance.search_and_download(
        query=query,
        output_dir=project_dir,
        num=limit,
        min_resolution=(res_x, res_y),
        cache_path=cache_filename,
        delay=delay,
        remove_no_alt=st.session_state.remove_no_cap,
        caption=caption,
    )
    msg.success("Scrape Complete!")
    print("Done.")


# ========================== Main Application Section ==========================
def main():
    st.set_page_config(page_title="Pinterest DL")
    init_state()
    query, project_name, res_x, res_y, image_limit, timeout, delay, mode, caption = setup_ui()
    project_dir = Path("downloads", project_name)

    col1, col2 = st.columns([0.5, 2])
    msg = st.empty()
    with col1:
        if st.button("Scrape", type="primary"):
            with st.spinner("Scraping..."):
                if mode == MODE_OPTIONS["Board"]:
                    scrape_images(
                        url=query,
                        project_name=project_name,
                        project_dir=project_dir,
                        res_x=res_x,
                        res_y=res_y,
                        limit=image_limit,
                        timeout=timeout,
                        delay=delay,
                        caption=caption,
                        msg=msg,
                    )
                elif mode == MODE_OPTIONS["Search"]:
                    search_images(
                        query=query,
                        project_name=project_name,
                        project_dir=project_dir,
                        res_x=res_x,
                        res_y=res_y,
                        limit=image_limit,
                        timeout=timeout,
                        delay=delay,
                        caption=caption,
                        msg=msg,
                    )
                else:
                    msg.error("Invalid mode selected!")

    with col2:
        if st.button("📂 Open Directory"):
            os.startfile(project_dir)

    footer()


if __name__ == "__main__":
    main()
