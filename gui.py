import os
import time
from pathlib import Path

import streamlit as st
from pinterest_dl import api


def disclaimer():
    st.markdown("---")
    st.info(
        "**⚠️ Disclaimer:**\n\n"
        "This project is independent and not affiliated with Pinterest. It's designed solely for educational purposes. "
        "Please be aware that automating the scraping of websites might conflict with their "
        "[Terms of Service](https://developers.pinterest.com/terms/). The repository owner disclaims any liability for misuse of this tool. "
        "Use it responsibly and at your own legal risk."
    )


def setup_ui():
    st.title("Pinterest Downloader")
    url = st.text_input("Pinterest URL", placeholder="https://www.pinterest.com/pin/1234567890/")
    project_name = st.text_input("Project Name", placeholder="Concept Art")
    with st.expander("Scrape Options"):
        res_x, res_y = quality_section()
        incognito, headful, browser, threshold, timeout = scraping_section()
    return url, project_name, res_x, res_y, incognito, headful, browser, threshold, timeout


def quality_section():
    col1, col2 = st.columns(2)
    with col1:
        res_x = st.number_input("Min Resolution X", 64, 4096, 512, step=64)
    with col2:
        res_y = st.number_input("Min Resolution Y", 64, 4096, 512, step=64)
    return res_x, res_y


def scraping_section():
    col1, col2 = st.columns(2)
    with col1:
        browser = st.selectbox("Web Driver", ["Chrome", "Firefox"])
    with col2:
        incognito = st.toggle("Incognito", False)
        headful = st.toggle("Headful", False)
    limit = st.slider("Image Count", 0, 800, 100, step=5)
    timeout = st.slider("Timeout (sec)", 0, 10, 3, step=1)
    return incognito, headful, browser, limit, timeout


# Logic
def scrape_images(
    url,
    project_name,
    project_dir,
    res_x,
    res_y,
    incognito,
    headful,
    browser,
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

    api.run_scrape(
        url,
        limit=limit,
        output=project_dir,
        timeout=timeout,
        json=True,
        json_path=cache_filename,
        firefox=(browser == "Firefox"),
        incognito=incognito,
        headful=headful,
        min_resolution=(res_x, res_y),
    )
    msg.success("Scrape Complete!")
    print("Done.")


def main():
    url, project_name, res_x, res_y, incognito, headful, browser, threshold, timeout = setup_ui()
    project_dir = Path("downloads", project_name)
    col1, col2 = st.columns([0.5, 2])
    msg = st.empty()
    with col1:
        if st.button("Scrape", type="primary"):
            with st.spinner("Scraping..."):
                scrape_images(
                    url,
                    project_name,
                    project_dir,
                    res_x,
                    res_y,
                    incognito,
                    headful,
                    browser,
                    threshold,
                    timeout,
                    msg,
                )

    with col2:
        if st.button("📂 Open Directory"):
            os.startfile(project_dir)

    disclaimer()


if __name__ == "__main__":
    main()
