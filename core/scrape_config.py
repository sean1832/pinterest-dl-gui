from dataclasses import dataclass


@dataclass
class ScrapeConfig:
    """Configuration for a pinterest-dl scrape operation."""

    url: str
    num: int
    output_dir: str
    min_resolution: tuple[int, int]
    delay: float
    download_streams: bool
    # How media is acquired: "scrape"/"search" hit Pinterest; "download" loads a previously
    # saved cache JSON whose path is carried in `url`.
    mode: str = "scrape"
    # When scraping, optionally persist the records to a cache JSON for later reuse.
    save_cache: bool = False
    cache_path: str | None = None  # empty -> auto metadata_<timestamp>.json under output_dir
    skip_download: bool = False  # scrape + save cache only; don't download media
    # TODO: implement in core and expose in UI
    caption_from_title: bool = False
    skip_remux: bool = False
    cookies: str | None = None
    ffmpeg_path: str | None = None
