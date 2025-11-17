from pathlib import Path

from bookmarks_to_shortcuts.raw import RawBookmarkFile
from bookmarks_to_shortcuts.tree import BookmarkTreeBuilder


def build_raw(tmp_path):
    data = {
        "roots": {
            "bookmark_bar": {
                "id": "1",
                "name": "Bookmarks Bar",
                "type": "folder",
                "children": [
                    {"id": "2", "name": "Docs", "type": "folder", "children": []},
                    {"id": "3", "name": "Example", "type": "url", "url": "https://example.com"},
                ],
            },
            "mobile": {"id": "4", "name": "Mobile", "type": "folder", "children": []},
        }
    }
    path = tmp_path / "Bookmarks"
    path.write_text(__import__("json").dumps(data), encoding="utf-8")
    return RawBookmarkFile.load(path)


def test_build_preserves_root_order(tmp_path):
    raw = build_raw(tmp_path)
    builder = BookmarkTreeBuilder(raw)
    nodes = builder.build()
    assert [node.name for node in nodes] == ["Bookmarks Bar", "Mobile"]
    assert nodes[0].children[0].name == "Docs"
