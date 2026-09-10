# Top News URLs

[![CI](https://github.com/notnews/top_news/actions/workflows/ci.yml/badge.svg)](https://github.com/notnews/top_news/actions/workflows/ci.yml)
[![Data](https://img.shields.io/badge/data-Dataverse-blue)](https://doi.org/10.7910/DVN/ZNAKK6)
[![Code license](https://img.shields.io/badge/code-MIT-green)](LICENSE)

An hourly collector of news URLs from eleven sources. URL arrays stay in Git, with one URL per line so later collection diffs show additions. Full-text Dataverse releases are historical artifacts.

## Data

| File | URLs at cleanup baseline (2026-09-10) |
|---|---:|
| `abc_urls.json` | 239,290 |
| `cbs_urls.json` | 158,285 |
| `cnn_urls.json` | 39,185 |
| `lat_urls.json` | 75,121 |
| `nbc_urls.json` | 98,135 |
| `npr_urls.json` | 67,363 |
| `nyt_urls.json` | 130,507 |
| `politico_urls.json` | 13,544 |
| `propub_urls.json` | 2,342 |
| `usat_urls.json` | 51,239 |
| `wapo_urls.json` | 93,794 |

Historical June 2023 and March 2025 full-text database releases: [doi:10.7910/DVN/ZNAKK6](https://doi.org/10.7910/DVN/ZNAKK6). These have different coverage from the current URL arrays.

Counts describe the releases or local files identified above. Dataverse metadata requests returned HTTP 403 on 2026-09-10, so historical release counts could not all be reverified.

## Column dictionary

| Format | Columns | Meaning |
|---|---|---|
| JSON arrays | One string per element | Original historical URL or normalized newly discovered URL |
| Parquet export | `site`, `url` (strings) | Source code and URL |
| Historical full-text SQLite | `url`, `source`, `publish_date`, `title`, `authors`, `text`, `extraction_date`, `domain` | Historical article extraction outputs; consult the release for table names |

New URL normalization retains scheme, host, and path, stripping query and fragment. `abcnews.com` and `abcnews.go.com` remain distinct. Existing values are preserved; their normalized forms participate in deduplication. Within each file, incoming URLs append in discovery order.

## Coverage and known gaps

CNN's old feed stopped updating around 2024-07-28; USA Today's around 2023-08-31, per the cleanup handoff. Those gaps run to cleanup and are not backfilled. Their replacements are news sitemaps; a sitemap only exposes a recent window. The other sources remain RSS.

Feed failures and empty/malformed documents are logged. A site succeeds if at least one configured feed succeeds; the command exits nonzero only if every requested site fails. A zero-addition success can simply mean all URLs were already present. The corpus grows continuously; the table is a dated baseline.

Obsolete full-text extraction and Google-search notebooks were removed. An exposed Google API credential was removed from branch history and must still be revoked by its owner; old clones and cached copies may retain it.

## Collection methods

| Period | Method |
|---|---|
| 2022–cleanup | Eleven independent RSS scripts; scheduled commits of JSON arrays |
| Cleanup onward | Shared collector, RSS plus CNN/USA Today news sitemaps, atomic JSON replacement |

The hourly workflow and package change together. Updates are serialized, stage only URL arrays, and rebase before pushing. Pull-request CI ignores URL-only changes; scheduled CI still checks dependency drift.

The pre-cleanup implementation is preserved at [44d7cfd9d7dbb4e5b26e7efcc0db0065bb6130c5](https://github.com/notnews/top_news/tree/44d7cfd9d7dbb4e5b26e7efcc0db0065bb6130c5). The collector updates the root `*_urls.json` arrays atomically; reruns deduplicate against the saved URLs. Pure parsers read saved responses without accessing the network. Fixture provenance is in [tests/fixtures/SOURCES.md](tests/fixtures/SOURCES.md).

## Usage

Python 3.12 or later and [uv](https://docs.astral.sh/uv/) are required. Run these commands from the repository root. Keep downloaded inputs and generated files under ignored `data/`.

### Install

```sh
uv sync --frozen --group dev
```

### Collect

```sh
uv run top-news update
uv run top-news update --site cnn
```

### Convert

```sh
uv run top-news to-parquet --out data/urls.parquet
```

### Upload

The `upload` command reads `DATAVERSE_API_TOKEN` from the environment and adds the specified file to Dataverse. It does not publish a dataset version.

```sh
uv run top-news upload data/urls.parquet
```

## Development

Run the local checks:

```sh
make check
```

This runs Ruff, formatting, pytest, and pre-commit. Run `make ci-docker` to check lint and tests in standard Python 3.12 and 3.14 Docker images. CI uses the same lockfile and checks. Install the Git hooks with `uv run pre-commit install`.

## Citation

Use [CITATION.cff](CITATION.cff) and cite the relevant [Dataverse release](https://doi.org/10.7910/DVN/ZNAKK6), including its version and DOI.

## License

Code is [MIT licensed](LICENSE). URL data are CC BY 4.0, as specified by the original citation metadata; see [the license terms](https://creativecommons.org/licenses/by/4.0/). Article text retains its owners' rights.

## Adjacent Repositories

- [notnews/good_nyt](https://github.com/notnews/good_nyt) — Patterns in NYT production from 1987 to 2007
- [notnews/fox_news_transcripts](https://github.com/notnews/fox_news_transcripts) — Fox News Transcripts 2003--2025
- [notnews/uk_not_news](https://github.com/notnews/uk_not_news) — Not News: Provision of Apolitical News in the British News Media
- [notnews/nbc_transcripts](https://github.com/notnews/nbc_transcripts) — NBC-hosted MSNBC transcripts 2008--2014
- [notnews/hard_news](https://github.com/notnews/hard_news) — The Softening of Network Television News
