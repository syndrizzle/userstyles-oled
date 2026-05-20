#!/usr/bin/env python3
import shutil
import subprocess
import tempfile
from pathlib import Path

UPSTREAM_REPO = "https://github.com/catppuccin/userstyles.git"
FORK_REPO = "syndrizzle/userstyles-oled"
RAW_LIB_URL = f"https://raw.githubusercontent.com/{FORK_REPO}/main/lib/lib.less"

ROOT = Path(__file__).resolve().parents[1]
STYLES = ROOT / "styles"
LIB = ROOT / "lib"

MOCHA_PALETTE_OLD = "@base: #1e1e2e; @mantle: #181825; @crust: #11111b;"
MOCHA_PALETTE_NEW = "@base: #020202; @mantle: #010101; @crust: #000000;"
MOCHA_FILTER_OLD = "@base: brightness(0) saturate(100%) invert(7%) sepia(23%) saturate(3759%) hue-rotate(219deg) brightness(67%) contrast(84%); @mantle: brightness(0) saturate(100%) invert(22%) sepia(29%) saturate(493%) hue-rotate(204deg) brightness(44%) contrast(102%); @crust: brightness(0) saturate(100%) invert(25%) sepia(44%) saturate(549%) hue-rotate(204deg) brightness(18%) contrast(96%);"
MOCHA_FILTER_NEW = "@base: brightness(0) saturate(100%) invert(0.8%); @mantle: brightness(0) saturate(100%) invert(0.4%); @crust: brightness(0) saturate(100%) invert(0%);"


def run(command: list[str], cwd: Path | None = None) -> None:
    _ = subprocess.run(command, cwd=cwd, check=True)


def replace_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    _ = shutil.copytree(src, dst)


def patch_text_files() -> None:
    text_suffixes = {".css", ".less", ".md", ".txt"}
    for base in (STYLES, LIB):
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in text_suffixes:
                continue
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".md":
                text = text.replace(
                    "https://raw.githubusercontent.com/catppuccin/userstyles/main/styles/",
                    f"https://raw.githubusercontent.com/{FORK_REPO}/main/styles/",
                )
            elif path.name == "catppuccin.user.less":
                text = text.replace(
                    "@namespace github.com/catppuccin/userstyles/styles/",
                    f"@namespace github.com/{FORK_REPO}/styles/",
                )
                text = text.replace(
                    "@updateURL https://github.com/catppuccin/userstyles/raw/main/styles/",
                    f"@updateURL https://github.com/{FORK_REPO}/raw/main/styles/",
                )
                text = text.replace(
                    "https://userstyles.catppuccin.com/lib/lib.less",
                    RAW_LIB_URL,
                )
            _ = path.write_text(text, encoding="utf-8")


def patch_oled_palette() -> None:
    lib_file = LIB / "lib.less"
    text = lib_file.read_text(encoding="utf-8")
    text = text.replace(MOCHA_PALETTE_OLD, MOCHA_PALETTE_NEW)
    text = text.replace(MOCHA_FILTER_OLD, MOCHA_FILTER_NEW)
    _ = lib_file.write_text(text, encoding="utf-8")

    libreddit_mocha = STYLES / "libreddit" / "pure-css" / "mocha.css"
    if libreddit_mocha.exists():
        text = libreddit_mocha.read_text(encoding="utf-8")
        text = text.replace(
            "--foreground: #11111b; /* crust */", "--foreground: #000000; /* crust */"
        )
        text = text.replace(
            "--background: #1e1e2e; /* base */", "--background: #020202; /* base */"
        )
        text = text.replace(
            "--outside: #11111b; /* crust */", "--outside: #000000; /* crust */"
        )
        text = text.replace(
            "--post: #11111b; /* crust */", "--post: #000000; /* crust */"
        )
        _ = libreddit_mocha.write_text(text, encoding="utf-8")


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        upstream = Path(temp) / "userstyles"
        run(["git", "clone", "--depth", "1", UPSTREAM_REPO, str(upstream)])

        replace_tree(upstream / "styles", STYLES)
        replace_tree(upstream / "lib", LIB)

    patch_text_files()
    patch_oled_palette()


if __name__ == "__main__":
    main()
