"""Minimal CLI harness for exporting Brave bookmarks."""
from __future__ import annotations

import argparse
from pathlib import Path

from .exporter import BookmarkExporter, DuplicateStrategy
from .raw import RawBookmarkFile
from .tree import BookmarkTreeBuilder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Brave bookmarks to .url files")
    parser.add_argument("bookmarks", type=Path, help="Path to Brave Bookmarks JSON file")
    parser.add_argument("output", type=Path, help="Output directory for exported shortcuts")
    parser.add_argument(
        "--include-roots",
        nargs="*",
        default=None,
        help="Optional list of Brave roots to export (bookmark_bar, other, synced, mobile)",
    )
    parser.add_argument(
        "--include-full-path",
        action="store_true",
        help="Include root names in exported directory paths",
    )
    parser.add_argument(
        "--duplicate-strategy",
        choices=[d.value for d in DuplicateStrategy],
        default=DuplicateStrategy.UNIQUE.value,
        help="How to handle duplicate filenames",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw = RawBookmarkFile.load(args.bookmarks)
    tree = BookmarkTreeBuilder(raw)
    nodes = tree.build(include_roots=args.include_roots)
    exporter = BookmarkExporter(
        output_root=args.output,
        include_full_path=args.include_full_path,
        duplicate_strategy=DuplicateStrategy(args.duplicate_strategy),
    )
    result = exporter.export(nodes)
    print(f"Created {len(result.created_files)} shortcuts; skipped {len(result.skipped)}")


if __name__ == "__main__":
    main()
