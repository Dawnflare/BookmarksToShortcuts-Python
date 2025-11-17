"""Convert raw bookmark JSON into typed nodes."""
from __future__ import annotations

from typing import Dict, List

from .model import BookmarkNode
from .raw import RawBookmarkFile


class BookmarkTreeBuilder:
    """Builds BookmarkNode hierarchies while preserving order."""

    ROOT_ORDER = [
        "bookmark_bar",
        "other",
        "synced",
        "mobile",
        "unknown",
    ]

    def __init__(self, raw: RawBookmarkFile):
        self.raw = raw

    def build(self, include_roots: List[str] | None = None) -> List[BookmarkNode]:
        roots = self.raw.roots()
        nodes: List[BookmarkNode] = []
        for key in self.ROOT_ORDER:
            if key not in roots:
                continue
            if include_roots and key not in include_roots:
                continue
            nodes.append(self._build_node(roots[key]))
        # include any additional custom roots deterministically
        for key in sorted(roots.keys()):
            if key in self.ROOT_ORDER:
                continue
            if include_roots and key not in include_roots:
                continue
            nodes.append(self._build_node(roots[key]))
        return nodes

    def _build_node(self, raw_node: Dict) -> BookmarkNode:
        node = BookmarkNode(
            id=str(raw_node.get("id", "")),
            name=raw_node.get("name", ""),
            type=raw_node.get("type", "folder" if raw_node.get("children") else "url"),
            url=raw_node.get("url"),
        )
        for child in raw_node.get("children", []):
            node.add_child(self._build_node(child))
        return node
