from pathlib import Path

from bookmarks_to_shortcuts.exporter import BookmarkExporter, DuplicateStrategy
from bookmarks_to_shortcuts.model import BookmarkNode


def make_sample_tree(tmp_path: Path) -> BookmarkNode:
    root = BookmarkNode(id="1", name="Bookmarks Bar", type="folder")
    sub = BookmarkNode(id="2", name="Work", type="folder")
    site = BookmarkNode(id="3", name="Example / Docs", type="url", url="https://example.com")
    dup = BookmarkNode(id="4", name="Example / Docs", type="url", url="https://example.org")
    sub.add_child(site)
    sub.add_child(dup)
    root.add_child(sub)
    return root


def test_export_creates_shortcuts(tmp_path):
    root = make_sample_tree(tmp_path)
    exporter = BookmarkExporter(tmp_path, include_full_path=False)
    result = exporter.export([root])
    assert len(result.created_files) == 2
    assert all(p.exists() for p in result.created_files)


def test_duplicate_strategy_unique(tmp_path):
    root = make_sample_tree(tmp_path)
    exporter = BookmarkExporter(tmp_path, include_full_path=False, duplicate_strategy=DuplicateStrategy.UNIQUE)
    result = exporter.export([root])
    names = sorted(p.name for p in result.created_files)
    assert names == ["Example _ Docs (2).url", "Example _ Docs.url"]


def test_empty_folders_are_skipped(tmp_path):
    root = BookmarkNode(id="1", name="Bookmarks Bar", type="folder")
    empty = BookmarkNode(id="2", name="Empty Folder", type="folder")
    root.add_child(empty)
    exporter = BookmarkExporter(tmp_path, include_full_path=False)
    result = exporter.export([root])
    assert not result.created_files
    assert not any(tmp_path.iterdir())
