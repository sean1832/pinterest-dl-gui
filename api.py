import json
import shutil
import threading
from pathlib import Path

from pinterest_dl import PinterestMedia

from core import events
from core.scrape_config import ScrapeConfig


class Api:
    """pywebview js_api surface exposed to the Svelte frontend."""

    def __init__(self) -> None:
        self._window = None  # set by app.py on create_window
        self._stop = threading.Event()  # cooperative cancel flag, checked in both phase loops
        self._thread: threading.Thread | None = None  # the active run thread, or None when idle

    def set_window(self, window) -> None:
        """Receive the window handle so the run thread can push events into JS."""
        self._window = window

    def _emit(self, event: events.Event) -> None:
        """Push one RunEvent into the frontend. Runs on the background thread."""
        if self._window is None:
            return
        # Double-encode: inner dumps -> a JSON string; outer dumps -> a safe JS string
        # literal, so log text with quotes/newlines can't break the evaluate_js call.
        payload = json.dumps(json.dumps(event))
        try:
            self._window.evaluate_js(f"window.__pdl_emit({payload})")
        except Exception:
            # the only known case is "WebView has been destroyed",
            # which can happen if the run thread is still winding down while the user closes the app
            pass

    def start_run(self, config: dict) -> dict:
        """Validate a run request and launch it on a daemon thread. Returns immediately."""
        url = str(config.get("url", "")).strip()
        if not url:
            self._emit(events.error("Source URL is required."))
            return {"success": False}

        if self._thread is not None and self._thread.is_alive():  # ensure single run at a time.
            self._emit(events.error("A run is already in progress. Please wait for it to finish."))
            return {"success": False}

        res_w, res_h = config["min_resolution"]  # JS sends [w, h]; unpack asserts length 2 at runt

        scrape_config = ScrapeConfig(
            url=url,
            num=int(config["num"]),
            output_dir=str(config["output_dir"]),
            min_resolution=(int(res_w), int(res_h)),
            delay=float(config["delay"]),
            download_streams=bool(config["download_streams"]),
            skip_remux=bool(config.get("skip_remux", False)),
            caption_from_title=bool(config.get("caption_from_title", False)),
        )

        self._stop.clear()  # reset any leftover cancel from a previous run
        self._thread = threading.Thread(target=self._run, args=(scrape_config,), daemon=True)
        self._thread.start()
        return {"success": True}

    def terminate(self) -> None:
        """Signal the active run to stop, if any. The run thread will check this between items."""
        self._stop.set()

    def _run(self, config: ScrapeConfig) -> None:
        """Execute one run (scrape -> download) on the background thread, emitting events"""
        from pinterest_dl import PinterestDL
        from pinterest_dl.download import USER_AGENT, MediaDownloader

        from core.downloader import run_api_scrape, run_download

        # Initialized up front so the cancel/except paths can report partial counts even if
        # never reach the download phase (media_list may not exists there)
        scraped = 0
        downloaded = 0
        videos = 0
        try:
            with events.forward_logs(self._emit):
                scraper = PinterestDL.with_api()
                downloader = MediaDownloader(user_agent=USER_AGENT, timeout=10, max_retries=3)

                # === scraping phase ===
                def on_progress(media):
                    nonlocal scraped
                    if self._stop.is_set():
                        raise events.RunCancelled()
                    scraped += 1
                    self._emit(events.progress("scrape", scraped, config.num))
                    self._emit(events.media(media.src, media.video_stream is not None))

                media_list = run_api_scrape(scraper, config, on_progress)

                # === ffmpeg guard: ===
                # downgrade videos -> images if remux needed but unavailable
                download_streams = config.download_streams
                if download_streams and not config.skip_remux and not self.check_ffmpeg()["found"]:
                    download_streams = False
                    self._emit(
                        events.log("warn", "FFmpeg not found; downloading images instead of videos")
                    )

                # === download phase ===
                total = len(media_list)

                def on_file_downloaded(index: int, media: PinterestMedia):
                    nonlocal downloaded, videos
                    downloaded = index + 1
                    if download_streams and media.video_stream is not None:
                        videos += 1
                    self._emit(events.progress("download", downloaded, total))

                run_download(
                    media_list,
                    downloader,
                    Path(config.output_dir),
                    download_streams,
                    config.skip_remux,
                    on_file_downloaded,
                    lambda: self._stop.is_set(),
                )
                if self._stop.is_set():  # cancelled between files
                    raise events.RunCancelled()
                self._emit(events.done(scraped, downloaded, videos))
        except events.RunCancelled:
            self._emit(events.log("info", "Run cancelled by user."))
            self._emit(events.done(scraped, downloaded, videos))
        except Exception as e:
            self._emit(events.error(f"An unexpected error occurred: {str(e)}"))
        finally:
            self._stop.clear()  # ensure reset for the next run, even if this one errored out
            self._thread = None  # mark no active run

    def get_core_version(self) -> str:
        """Get the version of the embedded pinterest-dl core."""
        # Import and call __version__ here to avoid importing pinterest_dl at the module level.
        from pinterest_dl import __version__

        return __version__

    def check_ffmpeg(self, custom_path: str | None = None) -> dict[str, bool | str]:
        """Resolve ffmpeg for the GUI's video-remux feature.

        Checks a custom override first, then PATH. `shutil.which` validates that
        the target exists and is executable, so the frontend can show
        Found / Not found without shelling out itself.
        """
        path = shutil.which(custom_path) if custom_path else shutil.which("ffmpeg")
        if path is None:
            return {"found": False, "path": ""}
        return {"found": True, "path": path}
