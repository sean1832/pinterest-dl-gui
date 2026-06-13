import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "frontend"
WEB_DIR = ROOT / "web"
NPM = "npm.cmd" if sys.platform == "win32" else "npm"  # npm is a .cmd script on Windows


def build_frontend():
    print(">>> Installing frontend dependencies...")
    subprocess.run([NPM, "install"], cwd=FRONTEND_DIR, check=True)

    print(">>> Building frontend...")
    subprocess.run([NPM, "run", "build"], cwd=FRONTEND_DIR, check=True)

    print(f">>> Frontend built -> {WEB_DIR}")


def build_release():
    # TODO: invoke Nuitka here
    print("Release packaging not yet implemented.")
    sys.exit(1)  # fail loudly so CI doesn't silently produce nothing


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the project")
    parser.add_argument(
        "--release",
        action="store_true",
        help="Also package an executable with PyInstaller after building the frontend",
    )
    args = parser.parse_args()
    build_frontend()
    if args.release:
        build_release()


if __name__ == "__main__":
    main()
