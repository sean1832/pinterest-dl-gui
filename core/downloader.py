from pathlib import Path
from typing import Callable, List, Optional

from pinterest_dl import ApiScraper, PinterestMedia
from pinterest_dl.download import MediaDownloader

from .scrape_config import ScrapeConfig


def run_api_scrape(
    scraper: ApiScraper,
    config: ScrapeConfig,
    on_progress: Optional[Callable[[PinterestMedia], None]],
) -> List[PinterestMedia]:
    """Run a pinterest-dl scrape operation"""
    return scraper.scrape(
        url=config.url,
        num=config.num,
        min_resolution=config.min_resolution,
        delay=config.delay,
        caption_from_title=config.caption_from_title,
        on_progress=on_progress,
    )


def run_download(
    media_list: List[PinterestMedia],
    downloader: MediaDownloader,
    output_dir: Path,
    download_videos: bool,
    skip_remux: bool,
    on_file_downloaded: Callable[[int, PinterestMedia], None],
    should_cancel: Callable[[], bool],
) -> List[Path]:
    """Download each scraped media in order, reporting and checking cancel between files."""
    downloaded_paths: List[Path] = []
    for i, media in enumerate(media_list):
        if should_cancel():  # checked before each file -> Terminate stops within one item
            break
        result = downloader.download(media, output_dir, download_videos, skip_remux)
        downloaded_paths.append(result)
        on_file_downloaded(i, media)  # drives download-phase progress + the live videos tally
    return downloaded_paths
