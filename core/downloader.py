from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Sequence

from pinterest_dl import ApiScraper, PinterestMedia
from pinterest_dl.common import io
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


def run_api_search(
    scraper: ApiScraper,
    config: ScrapeConfig,
    on_progress: Optional[Callable[[PinterestMedia], None]],
) -> List[PinterestMedia]:
    """Run a pinterest-dl search operation"""
    return scraper.search(
        query=config.url,  # search mode repurposes the url field to carry the query string
        num=config.num,
        min_resolution=config.min_resolution,
        delay=config.delay,
        caption_from_title=config.caption_from_title,
        on_progress=on_progress,
    )


def resolve_cache_path(cache_path: str | None, output_dir: str) -> Path:
    """Pick where to write the metadata cache: an explicit path if given, else an
    auto-timestamped file under the output dir. If the target already exists, append
    a numeric suffix (_1, _2, ...) so repeat runs don't overwrite."""
    if cache_path and cache_path.strip():
        base = Path(cache_path.strip())
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = Path(output_dir) / f"metadata_{timestamp}.json"

    if not base.exists():
        return base
    counter = 1
    while True:
        candidate = base.with_name(f"{base.stem}_{counter}{base.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def save_cache(media_list: Sequence[PinterestMedia], path: Path) -> None:
    """Serialize scraped media records to JSON for later reuse by download mode."""
    path.parent.mkdir(parents=True, exist_ok=True)
    io.write_json([media.to_dict() for media in media_list], str(path), indent=4)


def load_cache(path: Path) -> List[PinterestMedia]:
    """Rebuild media records from a previously saved cache JSON."""
    raw = io.read_json(str(path))
    records = raw if isinstance(raw, list) else [raw]
    return [PinterestMedia.from_dict(record) for record in records]


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
