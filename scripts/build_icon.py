"""Convert docs/designs/icon.svg -> assets/icon.ico via Edge + ImageMagick."""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVG = ROOT / "docs" / "designs" / "icon.svg"
OUT = ROOT / "assets" / "icon.ico"
SIZES = [256, 128, 64, 48, 32, 16]


def render_pngs(svg: Path, sizes: list[int], tmp: Path) -> list[Path]:
    from playwright.sync_api import sync_playwright

    svg_content = svg.read_text(encoding="utf-8")
    pngs: list[Path] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        for size in sizes:
            html = (
                f"<!DOCTYPE html><html><head><style>"
                f"html,body{{margin:0;padding:0;width:{size}px;height:{size}px;"
                f"background:transparent;overflow:hidden}}"
                f"</style></head><body>"
                + svg_content.replace(
                    'width="100%" height="100%"',
                    f'width="{size}" height="{size}"',
                )
                + "</body></html>"
            )
            html_file = tmp / f"icon_{size}.html"
            html_file.write_text(html, encoding="utf-8")

            page = browser.new_page(viewport={"width": size, "height": size})
            page.goto(html_file.as_uri())

            png = tmp / f"icon_{size}.png"
            page.screenshot(path=str(png), omit_background=True)
            pngs.append(png)
            print(f"  rendered {size}x{size}")
        browser.close()

    return pngs


def build_ico(pngs: list[Path], out: Path) -> None:
    if not shutil.which("magick"):
        sys.exit("error: ImageMagick 'magick' not found on PATH")
    args = ["magick"] + [str(p) for p in pngs] + ["-compress", "None", str(out)]
    subprocess.run(args, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build assets/icon.ico from SVG.")
    parser.add_argument("--svg", type=Path, default=SVG)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Rendering {args.svg} ...")
    with tempfile.TemporaryDirectory() as tmp:
        pngs = render_pngs(args.svg, SIZES, Path(tmp))
        print(f"Building {args.out} ...")
        build_ico(pngs, args.out)

    print(f"Done: {args.out}")


if __name__ == "__main__":
    main()
