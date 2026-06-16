import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Callable, List, Optional, Sequence

from PIL import Image
from pinterest_dl import ApiScraper, PinterestMedia
from pinterest_dl.common import io
from pinterest_dl.download import MediaDownloader
from pinterest_dl.scrapers import operations

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
    media_list: Sequence[PinterestMedia],
    downloader: MediaDownloader,
    output_dir: Path,
    download_videos: bool,
    skip_remux: bool,
    max_workers: int,
    on_file_downloaded: Callable[[int, PinterestMedia], None],
    on_file_failed: Callable[[int, PinterestMedia, Exception], None],
    should_cancel: Callable[[], bool],
) -> List[Path]:
    """Download scraped media concurrently, reporting completions on the calling thread.

    Downloads run on a thread pool, but callbacks fire here as futures complete, not in
    worker threads -- so counter mutation and event emission stay single-threaded and need
    no locks. `completed` is the running 1-based count, since completions arrive out of order.

    A single file failing is reported via on_file_failed and skipped, so one bad pin does
    not abort the batch. Cancellation drops un-started downloads; in-flight ones run to
    completion since a blocking download can't be interrupted.
    """
    downloaded_paths: List[Path] = []
    if not media_list:
        return downloaded_paths

    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_media = {
            executor.submit(
                downloader.download, media, output_dir, download_videos, skip_remux
            ): media
            for media in media_list
        }
        for future in as_completed(future_to_media):
            if should_cancel():
                # Drop everything not yet started; in-flight futures still finish as the
                # `with` block waits on shutdown. cancel() is a no-op on running futures.
                for pending in future_to_media:
                    pending.cancel()
                break
            media = future_to_media[future]
            completed += 1
            try:
                result = future.result()
            except Exception as e:
                on_file_failed(completed, media, e)  # warn + advance progress, then move on
                continue
            media.set_local_path(result)  # captioning reads local_path to find the saved file
            downloaded_paths.append(result)
            on_file_downloaded(completed, media)  # drives download progress + live videos tally
    return downloaded_paths


def thumbnail_data_uri(path: Path, max_edge: int = 104) -> str:
    """Build a small base64 JPEG data URI from a downloaded image, for the preview strip.

    The app page is served over http://127.0.0.1, so it can't load file:// paths, and
    pointing an <img> at the remote source would re-download every image. A data URI of
    the on-disk file avoids both. max_edge is 2x the 52px display box for retina sharpness.
    Returns "" when the file isn't a decodable image (e.g. a video), so the caller can fall
    back to a placeholder.
    """
    try:
        with Image.open(path) as img:
            img.draft("RGB", (max_edge, max_edge))  # let the JPEG decoder downscale up front
            img = img.convert("RGB")
            img.thumbnail((max_edge, max_edge))
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=80)
    except (OSError, ValueError):
        return ""
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def apply_captions(media_list: Sequence[PinterestMedia], output_dir: Path, caption: str) -> None:
    """Write captions for downloaded media: txt/json sidecars or embedded EXIF.

    Requires each media's local_path to be set (done by run_download). verbose=True
    disables pinterest_dl's tqdm progress bar, which has no console to draw to in the
    packaged windowed app; the debug logs it enables are filtered out by the INFO sink.
    """
    if caption == "none":
        return
    if caption in ("txt", "json"):
        operations.add_captions_to_file(media_list, output_dir, caption, verbose=True)
    elif caption == "metadata":
        operations.add_captions_to_meta(media_list, verbose=True)
    else:
        raise ValueError(f"Invalid caption mode: {caption!r}")
