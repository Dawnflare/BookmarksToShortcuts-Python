from pathlib import Path

from bookmarks_to_shortcuts.exporter import (
    BookmarkExporter,
    DuplicateStrategy,
    StructureMode,
)
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


def test_export_combined_writes_files_in_root(tmp_path):
    root = make_sample_tree(tmp_path)
    exporter = BookmarkExporter(
        tmp_path,
        include_full_path=False,
        structure_mode=StructureMode.COMBINED,
    )
    result = exporter.export([root])
    assert {p.parent for p in result.created_files} == {tmp_path}
    assert sorted(p.name for p in result.created_files) == [
        "Example _ Docs (2).url",
        "Example _ Docs.url",
    ]


def test_export_html_orders_sections(tmp_path):
    root = BookmarkNode(id="1", name="Bookmarks Bar", type="folder")
    alpha = BookmarkNode(id="2", name="Alpha", type="folder")
    work = BookmarkNode(id="3", name="Work", type="folder")
    zeta = BookmarkNode(id="4", name="Zeta", type="folder")
    apis = BookmarkNode(id="5", name="Apis", type="folder")

    alpha.add_child(
        BookmarkNode(id="6", name="Alpha Docs", type="url", url="https://alpha.example")
    )
    apis.add_child(
        BookmarkNode(id="7", name="API Reference", type="url", url="https://api.example")
    )
    work.add_child(apis)
    zeta.add_child(
        BookmarkNode(id="8", name="Zeta", type="url", url="https://zeta.example")
    )

    root.add_child(work)
    root.add_child(zeta)
    root.add_child(alpha)

    exporter = BookmarkExporter(tmp_path, include_full_path=False)
    html_path = tmp_path / "bookmarks.html"
    count = exporter.export_html([root], html_path)

    html = html_path.read_text()
    assert count == 3
    alpha_idx = html.index("<h2>Bookmarks Bar / Alpha</h2>")
    work_idx = html.index("<h2>Bookmarks Bar / Work / Apis</h2>")
    zeta_idx = html.index("<h2>Bookmarks Bar / Zeta</h2>")
    assert alpha_idx < work_idx < zeta_idx
    assert "Alpha Docs" in html
    assert "API Reference" in html


def test_export_html_combined_flat_list(tmp_path):
    root = make_sample_tree(tmp_path)
    exporter = BookmarkExporter(
        tmp_path,
        include_full_path=False,
        structure_mode=StructureMode.COMBINED,
    )
    html_path = tmp_path / "bookmarks.html"
    exporter.export_html([root], html_path)
    html = html_path.read_text()
    assert "<h2>" not in html
    assert html.count("<li>") == 2


def test_export_text_includes_sections(tmp_path):
    root = BookmarkNode(id="1", name="Bookmarks Bar", type="folder")
    misc = BookmarkNode(id="2", name="Misc", type="folder")
    misc.add_child(
        BookmarkNode(id="3", name="Notes", type="url", url="https://notes.example")
    )
    root.add_child(misc)

    exporter = BookmarkExporter(tmp_path, include_full_path=False)
    text_path = tmp_path / "bookmarks.txt"
    count = exporter.export_text([root], text_path)

    text = text_path.read_text().strip()
    assert count == 1
    assert text.splitlines()[0] == "Bookmarks Bar / Misc"
    assert "Notes - https://notes.example" in text


def test_export_text_combined_is_plain_list(tmp_path):
    root = make_sample_tree(tmp_path)
    exporter = BookmarkExporter(
        tmp_path,
        include_full_path=False,
        structure_mode=StructureMode.COMBINED,
    )
    text_path = tmp_path / "bookmarks.txt"
    exporter.export_text([root], text_path)
    text = text_path.read_text().strip().splitlines()
    assert text == ["https://example.com", "https://example.org"]
