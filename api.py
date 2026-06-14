import shutil


class Api:
    """pywebview js_api surface exposed to the Svelte frontend."""

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
