import logging
from contextlib import contextmanager
from typing import Any, Callable, Iterator, Literal

# Heterogenous wire payloads (str/int/bool vals).
Event = dict[str, Any]
Sink = Callable[[Event], None]

LogLevel = Literal["info", "warn", "error"]
Phase = Literal["scrape", "download"]


def progress(phase: Phase, current: int, total: int) -> Event:
    return {"type": "progress", "phase": phase, "current": current, "total": total}


def log(level: LogLevel, message: str) -> Event:
    return {"type": "log", "level": level, "message": message}


def media(thumbnail: str, is_video: bool) -> Event:
    return {"type": "media", "thumbnail": thumbnail, "is_video": is_video}


def done(scraped: int, downloaded: int, videos: int, saved: int = 0) -> Event:
    return {
        "type": "done",
        "scraped": scraped,
        "downloaded": downloaded,
        "videos": videos,
        "saved": saved,  # records written to a metadata cache (0 when not saving)
    }


def error(message: str) -> Event:
    return {"type": "error", "message": message}


class RunCancelled(Exception):
    """Unwinds a cancelled run from inside the scrape on_progress callback."""


def _level_name(level: int) -> LogLevel:
    if level >= logging.ERROR:
        return "error"
    elif level >= logging.WARNING:
        return "warn"
    else:
        return "info"


class LogForwarder(logging.Handler):
    """Bridges pinterest_dl's logging into the active run's event sink."""

    def __init__(self, sink: Sink):
        super().__init__()
        self.sink = sink

    def emit(self, record: logging.LogRecord) -> None:
        try:
            # getMessage render %-style args; record.msg along would not
            event = log(_level_name(record.levelno), record.getMessage())
            self.sink(event)
        except Exception:
            self.handleError(record)  # logging's own path; never bubble into the run thread


@contextmanager
def forward_logs(sink: Sink) -> Iterator[None]:
    """Context manager to forward logs from pinterest_dl to the given event sink."""
    logger = logging.getLogger("pinterest_dl")
    handler = LogForwarder(sink)
    handler.setLevel(logging.INFO)  # forward all levels; the sink can decide what to do with them
    previous_level = logger.level
    logger.addHandler(handler)

    # CRITICAL: the GUI never calls pinterest_dl.setup_logging(), so this logger is NOTSET
    # and inherits root's WARNING. Without lifting it to INFO, every INFO record is filtered
    # at the logger before the handler ever runs.
    logger.setLevel(logging.INFO)
    try:
        yield
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)  # restore, so a second run doesn't compound state
