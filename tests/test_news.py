import json
from pathlib import Path

import pytest

from top_news import cli, fetch, store

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize("host", ["abcnews.com", "abcnews.go.com"])
def test_normalization(host):
    assert fetch.normalize_url(f"https://{host}/a?q=1#b") == f"https://{host}/a"


def test_store_preserves_history_and_deduplicates(tmp_path):
    path = tmp_path / "urls.json"
    store.write(path, ["https://example.com/a?old=1"])
    assert store.update(
        path, ["https://example.com/a?new=2", "https://example.com/b"]
    ) == (1, 2)
    assert store.load(path) == ["https://example.com/a?old=1", "https://example.com/b"]
    assert len(path.read_text().splitlines()) == 4
    assert not list(tmp_path.glob("*.part"))
    before = path.read_bytes()
    assert store.update(path, ["https://example.com/b"])[0] == 0
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    ("kind", "file"), [("rss", "rss.xml"), ("news_sitemap", "sitemap.xml")]
)
def test_parsers(kind, file):
    assert fetch.parse_feed((FIXTURES / file).read_bytes(), kind)


@pytest.mark.parametrize("payload", [b"<html>error</html>", b"<rss><channel/></rss>"])
def test_bad_feed(payload):
    with pytest.raises(ValueError, match=r"malformed|no URLs"):
        fetch.parse_feed(payload, "rss")


def test_cli_partial_and_total_failure(tmp_path, monkeypatch):
    def fake(session, site):
        if site is cli.SITES["cnn"]:
            raise ValueError("down")
        return ["https://example.com/a"]

    monkeypatch.setattr(fetch, "fetch_site", fake)
    assert cli.update(tmp_path, ["cnn", "abc"]) == 0
    assert cli.update(tmp_path, ["cnn"]) == 1
    assert json.loads((tmp_path / "abc_urls.json").read_text()) == [
        "https://example.com/a"
    ]


def test_invalid_historical_values_do_not_block_updates(tmp_path):
    path = tmp_path / "urls.json"
    store.write(path, ["", "/historical-relative"])
    assert store.update(path, ["https://example.com/new"]) == (1, 3)
    assert store.load(path)[:2] == ["", "/historical-relative"]
