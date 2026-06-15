import json
import os
import shutil
import threading
import time
from email.utils import parsedate_to_datetime  # WebView2 hands back RFC-date expiry strings
from http.cookies import SimpleCookie
from pathlib import Path

import webview
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
        mode = str(config.get("mode", "scrape"))
        save_cache = bool(config.get("save_cache", False))
        skip_download = bool(config.get("skip_download", False))

        url = str(config.get("url", "")).strip()
        if not url:
            label = {"download": "A cache JSON file", "search": "A search query"}.get(
                mode, "Source URL"
            )
            self._emit(events.error(f"{label} is required."))
            return {"success": False}

        if mode == "download" and not Path(url).is_file():
            self._emit(events.error(f"Cache file not found: {url}"))
            return {"success": False}

        # Metadata-only only applies when scraping; download mode ignores both flags.
        if mode != "download" and skip_download and not save_cache:  # would produce nothing
            self._emit(events.error("Skip download requires Save metadata cache to be enabled."))
            return {"success": False}

        if self._thread is not None and self._thread.is_alive():  # ensure single run at a time.
            self._emit(events.error("A run is already in progress. Please wait for it to finish."))
            return {"success": False}

        res_w, res_h = config["min_resolution"]  # JS sends [w, h]; unpack asserts length 2 at runt

        scrape_config = ScrapeConfig(
            url=url,
            mode=mode,
            num=int(config["num"]),
            output_dir=str(config["output_dir"]),
            min_resolution=(int(res_w), int(res_h)),
            delay=float(config["delay"]),
            timeout=float(config.get("timeout", 10.0)),
            cookies=(str(config.get("cookies", "")).strip() or None),
            ensure_alt=bool(config.get("ensure_alt", False)),
            ffmpeg_path=(str(config.get("ffmpeg_path", "")).strip() or None),
            download_streams=bool(config["download_streams"]),
            skip_remux=bool(config.get("skip_remux", False)),
            caption_from_title=bool(config.get("caption_from_title", False)),
            caption=str(config.get("caption", "none")),
            save_cache=save_cache,
            cache_path=(str(config.get("cache_path", "")).strip() or None),
            skip_download=skip_download,
        )

        self._stop.clear()  # reset any leftover cancel from a previous run
        self._thread = threading.Thread(target=self._run, args=(scrape_config,), daemon=True)
        self._thread.start()
        return {"success": True}

    def terminate(self) -> None:
        """Signal the active run to stop, if any. The run thread will check this between items."""
        self._stop.set()

    def _run(self, config: ScrapeConfig) -> None:
        """Execute one run on the background thread, emitting events.

        Two shapes: download mode loads media from a cache JSON and downloads it;
        scrape/search mode scrapes Pinterest, optionally saves a cache JSON, and
        optionally stops there (metadata only) instead of downloading.
        """
        from pinterest_dl import PinterestDL
        from pinterest_dl.download import USER_AGENT, MediaDownloader

        from core.downloader import (
            apply_captions,
            load_cache,
            resolve_cache_path,
            run_api_scrape,
            run_api_search,
            run_download,
            save_cache,
            thumbnail_data_uri,
        )

        # Initialized up front so the cancel/except paths can report partial counts even if
        # never reach the download phase (media_list may not exists there)
        scraped = 0
        downloaded = 0
        videos = 0
        saved = 0
        try:
            with events.forward_logs(self._emit):
                downloader = MediaDownloader(
                    user_agent=USER_AGENT, timeout=config.timeout, max_retries=3
                )

                # === acquire media: load a cache file, or scrape Pinterest ===
                if config.mode == "download":
                    if self._stop.is_set():
                        raise events.RunCancelled()
                    media_list = load_cache(Path(config.url))
                    scraped = len(media_list)
                else:
                    scraper = PinterestDL.with_api(
                        timeout=config.timeout, ensure_alt=config.ensure_alt
                    )
                    # Cookies are optional; required only for private boards. Bad path/format
                    # raises here and surfaces as a run error rather than failing silently.
                    if config.cookies:
                        scraper.with_cookies_path(config.cookies)

                    def on_progress(media):
                        nonlocal scraped
                        if self._stop.is_set():
                            raise events.RunCancelled()
                        scraped += 1
                        self._emit(events.progress("scrape", scraped, config.num))

                    if config.mode == "scrape":
                        media_list = run_api_scrape(scraper, config, on_progress)
                    elif config.mode == "search":
                        media_list = run_api_search(scraper, config, on_progress)
                    else:
                        raise ValueError(f"Unsupported mode: {config.mode}")

                    # === optionally persist the scraped records for later reuse ===
                    if config.save_cache:
                        cache_path = resolve_cache_path(config.cache_path, config.output_dir)
                        save_cache(media_list, cache_path)
                        saved = len(media_list)
                        self._emit(events.log("info", f"Saved {saved} records to {cache_path}"))

                    # === metadata-only: stop before downloading ===
                    if config.skip_download:
                        self._emit(events.done(scraped, downloaded, videos, saved))
                        return

                # === ffmpeg guard: ===
                # downgrade videos -> images if remux needed but unavailable
                download_streams = config.download_streams
                if download_streams and not config.skip_remux:
                    ffmpeg = self.check_ffmpeg(config.ffmpeg_path)
                    if not ffmpeg["found"]:
                        download_streams = False
                        self._emit(
                            events.log(
                                "warn", "FFmpeg not found; downloading images instead of videos"
                            )
                        )
                    elif config.ffmpeg_path:
                        # The library invokes bare "ffmpeg" via subprocess, so a custom path is
                        # only honored if its directory is on PATH for the remux step.
                        ffmpeg_dir = str(Path(str(ffmpeg["path"])).parent)
                        path_entries = os.environ.get("PATH", "").split(os.pathsep)
                        if ffmpeg_dir not in path_entries:
                            os.environ["PATH"] = (
                                ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
                            )

                # === download phase ===
                total = len(media_list)
                self._emit(events.progress("download", 0, total))  # flip phase label to Downloading

                def on_file_downloaded(index: int, media: PinterestMedia):
                    nonlocal downloaded, videos
                    downloaded = index + 1
                    is_video_file = download_streams and media.video_stream is not None
                    if is_video_file:
                        videos += 1
                    self._emit(events.progress("download", downloaded, total))
                    # Preview the file just written to disk; a video stream has no still to show.
                    thumbnail = "" if is_video_file else thumbnail_data_uri(media.local_path)
                    self._emit(events.media(thumbnail, is_video_file))

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

                # === captions: write sidecars / embed EXIF for the downloaded files ===
                if config.caption != "none":
                    apply_captions(media_list, Path(config.output_dir), config.caption)
                    self._emit(events.log("info", f"Wrote captions ({config.caption})"))

                self._emit(events.done(scraped, downloaded, videos, saved))
        except events.RunCancelled:
            self._emit(events.log("info", "Run cancelled by user."))
            self._emit(events.done(scraped, downloaded, videos, saved))
        except Exception as e:
            self._emit(events.error(f"An unexpected error occurred: {str(e)}"))
        finally:
            self._stop.clear()  # ensure reset for the next run, even if this one errored out
            self._thread = None  # mark no active run

    def capture_cookies(self) -> dict:
        """
        Open a Pinterest login window, wait for the auth cookie, and save it as a cookies JSON.
        Runs on the `js_api` worker thread;
        blocking here is fine and keeps the GUI responsive.

        Returns:
            dict: {"success": bool, "path": str, "message": str}
        """
        if self._window is None:
            return {"success": False, "path": "", "message": "Window not initialized."}

        login_window = webview.create_window(
            "Login to Pinterest",
            "https://www.pinterest.com/login/",
            width=520,
            height=720,
        )
        if login_window is None:
            return {"success": False, "path": "", "message": "Failed to create login window."}

        # The user may give up and close the window. Treat that as a clean cancel rather than an error.
        closed = threading.Event()
        login_window.events.closed += lambda: closed.set()

        cookies: list[dict] = []
        deadline = time.monotonic() + 300  # 5 min cap so a walked-away user can't hang the thread
        while not closed.is_set() and time.monotonic() < deadline:
            try:
                raw = (
                    login_window.get_cookies()
                )  # blocks until cookies are available or the window is closed
            except Exception:
                break  # window torn down mid-call. Closed handler will also fire.

            if self._is_authenticated(raw):
                for cookie in raw:
                    if "pinterest.com" in self._cookie_domain(cookie):
                        cookies.append(self._to_pdl_cookie(cookie))
                break

            # poll every second until we see the auth cookie or the window is closed
            time.sleep(1.0)

        if not closed.is_set():
            login_window.destroy()  # close the login window if it's still open

        if not cookies:
            return {
                "success": False,
                "path": "",
                "message": "Login cancelled or authentication failed.",
            }

        target = self._file_dialog(
            webview.FileDialog.SAVE,
            directory=".",
            save_filename="cookies.json",
            file_types=("JSON File (*.json)", "All files (*.*)"),
        )
        if not target:
            return {"success": False, "path": "", "message": "Save cancelled."}

        Path(target).write_text(json.dumps(cookies, indent=2), encoding="utf-8")
        return {"success": True, "path": target, "message": f"Saved {len(cookies)} cookies."}

    @staticmethod
    def _cookie_domain(cookie: SimpleCookie) -> str:
        # pywebview returns http.cookies.SimpleCookie, one morsel each
        _, morsel = next(iter(cookie.items()))
        return morsel["domain"] or ""

    @staticmethod
    def _is_authenticated(cookies: list[SimpleCookie]) -> bool:
        # _pinterest_sess exists for anonymous visitors too; _auth=1 is the real login flag
        for cookie in cookies:
            name, morsel = next(iter(cookie.items()))
            if name == "_auth" and morsel.value == "1":
                return True
        return False

    @staticmethod
    def _to_pdl_cookie(cookie: SimpleCookie) -> dict:
        # map a SimpleCookie morsel to pinterest-dl's on-disk format (CookieJar.from_cookies)
        name, morsel = next(iter(cookie.items()))
        expires = morsel["expires"]
        expiry = None
        if expires:
            try:
                expiry = int(parsedate_to_datetime(expires).timestamp())
            except (TypeError, ValueError):
                pass  # if the date is malformed, just omit the expiry rather than failing outright

        return {
            "name": name,
            "value": morsel.value,
            "domain": morsel["domain"],
            "path": morsel["path"] or "/",
            "secure": bool(morsel["secure"]),
            "expiry": expiry,
        }

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

    def _file_dialog(
        self,
        dialog_type: int,
        directory: str,
        save_filename: str = "",
        file_types: tuple[str, ...] = (),
    ) -> str:
        """Run a native file dialog and return a single path, or "" if cancelled."""
        if self._window is None:
            return ""
        result = self._window.create_file_dialog(
            dialog_type,
            directory=directory,
            save_filename=save_filename,
            file_types=file_types,
        )
        if not result:  # None or empty tuple -> cancelled
            return ""
        # Dialogs return a single path typed as a sequence on some GUI backends; normalize.
        return result if isinstance(result, str) else str(result[0])

    def select_cache_file(self, default_path: str = "") -> str:
        """Save-file dialog: where to write the metadata cache JSON."""
        target = Path(default_path) if default_path.strip() else Path("metadata.json")
        return self._file_dialog(
            webview.FileDialog.SAVE,
            directory=str(target.parent),
            save_filename=target.name,
            file_types=("JSON File (*.json)", "All files (*.*)"),
        )

    def select_json_file(self, default_path: str = "") -> str:
        """Open-file dialog: pick an existing cache JSON for Download mode."""
        start = Path(default_path.strip()) if default_path.strip() else Path(".")
        directory = str(start.parent if start.suffix else start)
        return self._file_dialog(
            webview.FileDialog.OPEN,
            directory=directory,
            file_types=("JSON File (*.json)", "All files (*.*)"),
        )

    def select_folder(self, default_path: str = "") -> str:
        """Folder dialog: pick the output directory."""
        return self._file_dialog(webview.FileDialog.FOLDER, directory=default_path.strip() or ".")

    def select_file(self, default_path: str = "") -> str:
        """Open-file dialog: pick any file (used for ffmpeg executable, cookies JSON, etc.)."""
        start = Path(default_path.strip()) if default_path.strip() else Path(".")
        directory = str(start.parent if start.is_file() else start)
        return self._file_dialog(
            webview.FileDialog.OPEN, directory=directory, file_types=("All files (*.*)",)
        )
