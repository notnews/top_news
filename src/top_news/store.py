"""Preserve historical URL arrays and append normalized new URLs atomically."""

import json
import logging
from pathlib import Path

from top_news.fetch import normalize_url


def load(path: Path) -> list[str]:
    """Read a JSON URL array without silently accepting another data shape."""
    values = json.loads(path.read_text()) if path.exists() else []
    if not isinstance(values, list) or any(not isinstance(url, str) for url in values):
        raise ValueError(f"expected a URL array: {path}")
    return values


def write(path: Path, urls: list[str]) -> None:
    """Write one URL per line through a temporary sibling file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_suffix(path.suffix + ".part")
    part.write_text(json.dumps(urls, indent=0, ensure_ascii=False) + "\n")
    part.replace(path)


def update(path: Path, incoming: list[str]) -> tuple[int, int]:
    """Append new normalized URLs, retaining existing values and order."""
    urls = load(path)
    seen = set()
    invalid = 0
    for url in urls:
        try:
            seen.add(normalize_url(url))
        except ValueError:
            invalid += 1
    if invalid:
        logging.getLogger(__name__).warning(
            "%s: preserving %d historical values that are not absolute URLs",
            path,
            invalid,
        )
    added = 0
    for url in incoming:
        normalized = normalize_url(url)
        if normalized not in seen:
            seen.add(normalized)
            urls.append(normalized)
            added += 1
    if added or not path.exists():
        write(path, urls)
    return added, len(urls)
