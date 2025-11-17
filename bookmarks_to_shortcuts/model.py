"""Domain models for Brave bookmark exports."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional


@dataclass
class BookmarkNode:
    """Represents either a folder or a bookmark entry."""

    id: str
    name: str
    type: str  # "folder" or "url"
    url: Optional[str] = None
    children: List["BookmarkNode"] = field(default_factory=list)
    parent: Optional["BookmarkNode"] = field(default=None, repr=False)

    def add_child(self, child: "BookmarkNode") -> None:
        child.parent = self
        self.children.append(child)

    @property
    def is_folder(self) -> bool:
        return self.type == "folder"

    @property
    def path_components(self) -> List[str]:
        node: Optional[BookmarkNode] = self
        comps: List[str] = []
        while node is not None:
            comps.append(node.name)
            node = node.parent
        comps.reverse()
        return comps

    def iter_descendants(self) -> Iterable["BookmarkNode"]:
        for child in self.children:
            yield child
            yield from child.iter_descendants()
