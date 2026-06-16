import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "frontend"
WEB_DIR = ROOT / "web"
DIST_DIR = ROOT / "dist"
DIST_FOLDER = DIST_DIR / "app.dist"  # Nuitka names the standalone folder after app.py
PACKAGE_JSON = FRONTEND_DIR / "package.json"
ISS_SCRIPT = ROOT / "installer.iss"
EXE_NAME = "pinterest-dl.exe" if sys.platform == "win32" else "pinterest-dl"
EXE_SUFFIX = ".exe" if sys.platform == "win32" else ""
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


def get_version() -> str:
    text = PACKAGE_JSON.read_text(encoding="utf-8")
    match = re.search(r'"version":\s*"([^"]*)"', text)
    if match is None:
        raise RuntimeError(f"could not find a 'version' field in {PACKAGE_JSON}")
    return match.group(1)


def arch_tag() -> str:
    # Nuitka compiles for the host architecture, so label artifacts after the
    # machine running the build.
    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64"):
        return "x64"
    if machine in ("arm64", "aarch64"):
        return "arm64"
    return machine or "unknown"


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
        raise RuntimeError(
            "Nuitka is required for --release builds but is not installed. "
            "Install the build dependencies with: pip install -r requirements-build.txt"
        )


def build_release(*, console: bool = False, one_file: bool = False) -> None:
    _ensure_nuitka()
    DIST_DIR.mkdir(exist_ok=True)

    # --onefile bundles everything into a single exe that unpacks to a temp dir on
    # every launch (slower startup) but is fully portable. --standalone produces a
    # folder that runs in place with no unpacking, so it is the faster default.
    # --onefile implies --standalone; without either, Nuitka builds an accelerated
    # exe that depends on the local Python install and will not run elsewhere.
    cmd = [
        sys.executable, "-m", "nuitka",
        "--onefile" if one_file else "--standalone",
        # Auto-confirm tool downloads (e.g. the Windows dependency walker) so
        # non-interactive CI builds do not stall on a prompt and abort.
        "--assume-yes-for-downloads",
        f"--include-data-dir={WEB_DIR}=web",
        f"--include-data-dir={ROOT / 'assets'}=assets",
        # Ship the Apache-2.0 license (required for redistribution) and the EULA
        # so both are present in the standalone folder and the portable zip.
        f"--include-data-files={ROOT / 'LICENSE'}=LICENSE",
        f"--include-data-files={ROOT / 'EULA.txt'}=EULA.txt",
        f"--output-dir={DIST_DIR}",
        f"--output-filename={EXE_NAME}",
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

    # Standalone builds land in <dist>/app.dist/ alongside their dependencies;
    # onefile builds emit a single exe directly into <dist>.
    out_path = DIST_DIR / EXE_NAME if one_file else DIST_FOLDER / EXE_NAME
    print(f">>> Built -> {out_path}")


def build_zip(version: str) -> Path:
    """Zip the standalone folder into a portable, grab-and-run archive."""
    if not DIST_FOLDER.is_dir():
        raise RuntimeError(
            f"standalone build not found at {DIST_FOLDER}; run a --release build first"
        )

    stem = f"pinterest-dl-gui_{version}_{arch_tag()}"
    zip_path = DIST_DIR / f"{stem}.zip"
    # Nest everything under a clean top-level folder so extracting does not spray
    # files into the user's current directory.
    root = Path(stem)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(DIST_FOLDER.rglob("*")):
            if path.is_file():
                archive.write(path, root / path.relative_to(DIST_FOLDER))

    print(f">>> Zipped -> {zip_path}")
    return zip_path


def _find_iscc() -> Path:
    found = shutil.which("ISCC")
    if found is not None:
        return Path(found)

    # Inno Setup does not add ISCC to PATH by default, so probe its standard
    # install locations before giving up. Prefer the newest version installed.
    program_dirs = [
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
    ]
    for version_dir in ("Inno Setup 7", "Inno Setup 6"):
        for base in program_dirs:
            iscc = base / version_dir / "ISCC.exe"
            if iscc.is_file():
                return iscc

    raise RuntimeError(
        "Inno Setup compiler (ISCC.exe) not found. Install Inno Setup 6 or 7 from "
        "https://jrsoftware.org/isdl.php to build the installer."
    )


def build_installer(version: str) -> Path:
    """Wrap the standalone folder in an Inno Setup installer (Windows only)."""
    if sys.platform != "win32":
        raise RuntimeError("the installer build is only supported on Windows")
    if not DIST_FOLDER.is_dir():
        raise RuntimeError(
            f"standalone build not found at {DIST_FOLDER}; run a --release build first"
        )

    arch = arch_tag()
    iscc = _find_iscc()
    # installer.iss builds its OutputBaseFilename from these defines, so the exe
    # name stays in sync with the zip produced by build_zip.
    cmd = [str(iscc), f"/DAppVersion={version}", f"/DArch={arch}", str(ISS_SCRIPT)]

    print(">>> Building installer with Inno Setup...")
    subprocess.run(cmd, cwd=ROOT, check=True)

    out_path = DIST_DIR / f"pinterest-dl-gui_{version}_{arch}_setup.exe"
    print(f">>> Installer -> {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the project")
    parser.add_argument(
        "--release",
        action="store_true",
        help="Also package the app with Nuitka (standalone folder) after building the frontend",
    )
    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Build a single portable exe (slower startup). Independent of "
        "--release; combine with --zip/--installer to produce every artifact",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Zip the standalone folder into a portable archive (implies --release)",
    )
    parser.add_argument(
        "--installer",
        action="store_true",
        help="Build a Windows installer from the standalone folder with Inno Setup "
        "(implies --release)",
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

    # --onefile and the standalone folder need separate Nuitka compiles: a onefile
    # build's app.dist holds a DLL payload, not a runnable exe, so it cannot be
    # reused for --zip/--installer. The second compile reuses Nuitka's C build cache
    # in app.build, so it is far cheaper than a cold build. Build onefile first so
    # the standalone pass leaves a runnable app.dist on disk for --release.
    if args.onefile:
        build_release(console=args.console, one_file=True)
        # Give the portable exe the same name scheme as the zip/installer instead
        # of the bare pinterest-dl.exe that Nuitka emits.
        portable = DIST_DIR / f"pinterest-dl-gui_{get_version()}_{arch_tag()}_portable{EXE_SUFFIX}"
        portable.unlink(missing_ok=True)
        (DIST_DIR / EXE_NAME).rename(portable)
        print(f">>> Portable exe -> {portable}")

    if args.release or args.zip or args.installer:
        build_release(console=args.console, one_file=False)
        version = get_version()
        if args.zip:
            build_zip(version)
        if args.installer:
            build_installer(version)


if __name__ == "__main__":
    main()
