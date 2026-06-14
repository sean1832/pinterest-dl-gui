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
    # TODO: implement in core and expose in UI
    caption_from_title: bool = False
    skip_remux: bool = False
    cookies: str | None = None
    ffmpeg_path: str | None = None
