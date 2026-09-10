"""Command-line collector, Parquet export, and Dataverse upload."""

import argparse
import logging
import sys
from pathlib import Path

from top_news import fetch, store, upload
from top_news.sites import SITES


def update(directory: Path, names: list[str], session=None) -> int:
    """Report each site; return nonzero only if all requested sites failed."""
    session = session or fetch.make_session()
    succeeded = 0
    sys.stdout.write("site        added       total  status\n")
    for name in names:
        try:
            incoming = fetch.fetch_site(session, SITES[name])
            added, total = store.update(directory / f"{name}_urls.json", incoming)
        except Exception as exc:
            logging.getLogger(__name__).warning("%s: %s", name, exc)
            sys.stdout.write(f"{name:<10}       -           -  failed\n")
            continue
        succeeded += 1
        sys.stdout.write(f"{name:<10} {added:>6} {total:>11}  ok\n")
    return int(not succeeded)


def main(argv: list[str] | None = None) -> int:
    """Run a collection or export command."""
    parser = argparse.ArgumentParser(prog="top-news")
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("update")
    command.add_argument("--site", choices=sorted(SITES))
    command.add_argument("--directory", type=Path, default=Path())
    command = sub.add_parser("to-parquet")
    command.add_argument("--directory", type=Path, default=Path())
    command.add_argument("--out", type=Path, required=True)
    command = sub.add_parser("upload")
    command.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    if args.command == "update":
        return update(args.directory, [args.site] if args.site else list(SITES))
    if args.command == "upload":
        sys.stdout.write(upload.upload(args.file) + "\n")
        return 0
    import pyarrow as pa
    import pyarrow.parquet as pq

    rows = [
        {"site": name, "url": url}
        for name in SITES
        for url in dict.fromkeys(store.load(args.directory / f"{name}_urls.json"))
    ]
    schema = pa.schema(
        [
            pa.field("site", pa.string(), nullable=False),
            pa.field("url", pa.string(), nullable=False),
        ]
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        pa.Table.from_pylist(rows, schema=schema), args.out, compression="zstd"
    )
    sys.stdout.write(f"rows: {len(rows)}\n")
    return 0
