"""Check local image references used by the documentation sources.

The checker reports missing local images before Quarto renders the site. Set
IMAGE_CHECK_STRICT=1 (or pass --strict) to make missing files fail the build.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SOURCE_SUFFIXES = {".qmd", ".md", ".ipynb", ".css"}
IGNORED_DIRS = {
    ".git",
    ".quarto",
    ".venv",
    "venv",
    "_site",
    "client_examples",
    "jupyterlite",
}
IMAGE_SUFFIXES = {".avif", ".bmp", ".gif", ".ico", ".jpeg", ".jpg", ".png", ".svg", ".webp"}

MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\((?:<(?P<angle>[^>]+)>|(?P<plain>[^\s)]+))")
HTML_IMAGE = re.compile(r"<img\b[^>]*?\bsrc\s*=\s*(['\"])(?P<value>.*?)\1", re.IGNORECASE | re.DOTALL)
CSS_URL = re.compile(r"url\(\s*(?:(['\"])(?P<quoted>.*?)\1|(?P<plain>[^)\s]+))\s*\)", re.IGNORECASE)
FRONT_MATTER_IMAGE = re.compile(r"^\s*image\s*:\s*(?:['\"](?P<quoted>[^'\"]+)['\"]|(?P<plain>\S+))\s*$", re.MULTILINE)


def source_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        if any(part in IGNORED_DIRS for part in path.relative_to(ROOT).parts):
            continue
        files.append(path)
    return files


def references(text: str, suffix: str):
    if suffix == ".css":
        patterns = (CSS_URL,)
    else:
        patterns = (MARKDOWN_IMAGE, HTML_IMAGE, FRONT_MATTER_IMAGE)

    for pattern in patterns:
        for match in pattern.finditer(text):
            value = next((group for group in match.groupdict().values() if group), "")
            yield value, text.count("\n", 0, match.start()) + 1


def local_path(value: str, source: Path) -> Path | None:
    value = value.strip()
    if not value or "{{<" in value or "{{%" in value:
        return None

    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or value.startswith("//") or value.startswith("data:"):
        return None

    path_text = unquote(parsed.path)
    if not path_text or Path(path_text).suffix.lower() not in IMAGE_SUFFIXES:
        return None

    return ROOT / path_text.lstrip("/") if path_text.startswith("/") else source.parent / path_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Report missing local image references.")
    parser.add_argument("--strict", action="store_true", help="Exit with an error when images are missing.")
    args = parser.parse_args()
    strict = args.strict or os.getenv("IMAGE_CHECK_STRICT") == "1"

    missing: list[tuple[Path, int, str]] = []
    seen: set[tuple[Path, int, str]] = set()

    for source in source_files():
        text = source.read_text(encoding="utf-8", errors="replace")
        for value, line in references(text, source.suffix.lower()):
            candidate = local_path(value, source)
            if candidate is None or candidate.is_file():
                continue
            item = (source.relative_to(ROOT), line, value)
            if item not in seen:
                seen.add(item)
                missing.append(item)

    if not missing:
        print("Image check: all local image references were found.")
        return 0

    for source, line, value in missing:
        print(f"WARNING: missing image: {source}:{line}: {value}")
    print(f"Image check: {len(missing)} missing local image reference(s).")
    if strict:
        print("Image check failed because strict mode is enabled.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())