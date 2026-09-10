"""Retrieve and parse RSS feeds and news sitemaps."""

import logging
from urllib.parse import urlsplit, urlunsplit
from xml.etree import ElementTree as ET

import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger(__name__)


def normalize_url(url: str) -> str:
    """Keep scheme, host and path; discard query and fragment."""
    parts = urlsplit(url.strip())
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ValueError(f"not an HTTP URL: {url!r}")
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path, "", ""))


def parse_feed(payload: bytes, kind: str) -> list[str]:
    """Return article URLs, rejecting malformed or empty source documents."""
    if kind == "rss":
        feed = feedparser.parse(payload)
        if feed.bozo:
            raise ValueError(f"malformed RSS: {feed.bozo_exception}")
        urls = [entry.link for entry in feed.entries if entry.get("link")]
    elif kind == "news_sitemap":
        if b"<!DOCTYPE" in payload.upper() or b"<!ENTITY" in payload.upper():
            raise ValueError("XML declarations are not allowed in sitemaps")
        root = ET.fromstring(payload)  # noqa: S314 - declarations rejected above
        if root.tag.rsplit("}", 1)[-1] != "urlset":
            raise ValueError("expected a news sitemap urlset")
        urls = [node.text for node in root.findall("{*}url/{*}loc") if node.text]
    else:
        raise ValueError(f"unknown source kind: {kind}")
    if not urls:
        raise ValueError("source contained no URLs")
    return list(dict.fromkeys(normalize_url(url) for url in urls))


def make_session() -> requests.Session:
    """Create a session with bounded retries and explicit request timeouts."""
    session = requests.Session()
    session.headers["User-Agent"] = (
        "top-news/1.0 (+https://github.com/notnews/top_news)"
    )
    retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    for scheme in ("https://", "http://"):
        session.mount(scheme, HTTPAdapter(max_retries=retry))
    return session


def fetch_site(session, site: dict) -> list[str]:
    """Collect working feeds; fail the site only if none of its feeds worked."""
    urls = []
    successes = 0
    for feed_url in site["urls"]:
        try:
            response = session.get(feed_url, timeout=30)
            response.raise_for_status()
            urls.extend(parse_feed(response.content, site["kind"]))
            successes += 1
        except (requests.RequestException, ValueError, ET.ParseError) as exc:
            log.warning("%s: %s", feed_url, exc)
    if not successes:
        raise ValueError("all feeds failed or were empty")
    return list(dict.fromkeys(urls))
