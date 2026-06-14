import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "frontend"
WEB_DIR = ROOT / "web"
PACKAGE_JSON = FRONTEND_DIR / "package.json"
NPM = "npm.cmd" if sys.platform == "win32" else "npm"  # npm is a .cmd script on Windows


def set_version(version: str) -> None:
    # Rewrite only the "version" line so the rest of package.json keeps its exact
    # formatting (json round-tripping would reorder keys and reindent the file).
    text = PACKAGE_JSON.read_text(encoding="utf-8")
    new_text, count = re.subn(
        r'("version":\s*")[^"]*(")', rf"\g<1>{version}\g<2>", text, count=1
    )
    if count != 1:
        raise RuntimeError(f"could not find a 'version' field in {PACKAGE_JSON}")
    PACKAGE_JSON.write_text(new_text, encoding="utf-8")
    print(f">>> Set frontend version -> {version}")


def build_frontend():
    print(">>> Installing frontend dependencies...")
    subprocess.run([NPM, "install"], cwd=FRONTEND_DIR, check=True)

    print(">>> Building frontend...")
    subprocess.run([NPM, "run", "build"], cwd=FRONTEND_DIR, check=True)

    print(f">>> Frontend built -> {WEB_DIR}")


def _ensure_nuitka() -> None:
    try:
        import nuitka  # noqa: F401
    except ImportError:
        print(">>> Nuitka not found, installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "nuitka"], check=True)


def build_release(*, console: bool = False) -> None:
    _ensure_nuitka()
    dist_dir = ROOT / "dist"
    dist_dir.mkdir(exist_ok=True)

    exe_name = "pinterest-dl.exe" if sys.platform == "win32" else "pinterest-dl"

    cmd = [
        sys.executable, "-m", "nuitka",
        "--onefile",
        f"--include-data-dir={WEB_DIR}=web",
        f"--include-data-dir={ROOT / 'assets'}=assets",
        f"--output-dir={dist_dir}",
        f"--output-filename={exe_name}",
    ]

    if sys.platform == "win32":
        console_mode = "force" if console else "disable"
        cmd += [
            f"--windows-console-mode={console_mode}",
            f"--windows-icon-from-ico={ROOT / 'assets' / 'icon.ico'}",
            # Nuitka 4.1.2's pywebview plugin whitelists the Windows backend modules
            # but omits webview.platforms.win32, the helper that winforms.py imports,
            # so it wrongly excludes it and the exe dies at startup. Disable the plugin
            # and include the Windows backend ourselves. Data files (webview js/lib,
            # WebView2 + pythonnet DLLs) come from Nuitka's package config, not the
            # plugin, so disabling it does not drop them.
            "--disable-plugin=pywebview",
            "--include-module=webview.platforms.winforms",
            "--include-module=webview.platforms.win32",
            "--include-module=webview.platforms.edgechromium",
            # The remaining backends pull in deps we do not ship (PyObjC, gi, qt, cef).
            "--nofollow-import-to=webview.platforms.cocoa",
            "--nofollow-import-to=webview.platforms.gtk",
            "--nofollow-import-to=webview.platforms.qt",
            "--nofollow-import-to=webview.platforms.android",
            "--nofollow-import-to=webview.platforms.cef",
        ]

    cmd.append(str(ROOT / "app.py"))

    print(">>> Compiling with Nuitka...")
    subprocess.run(cmd, cwd=ROOT, check=True)
    print(f">>> Built -> {dist_dir / exe_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the project")
    parser.add_argument(
        "--release",
        action="store_true",
        help="Also package a single executable with Nuitka after building the frontend",
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Enable console window in the packaged exe (useful for debugging)",
    )
    parser.add_argument(
        "--version",
        help="Write this version into frontend/package.json before building",
    )
    args = parser.parse_args()
    if args.version:
        set_version(args.version)
    build_frontend()
    if args.release:
        build_release(console=args.console)


if __name__ == "__main__":
    main()
