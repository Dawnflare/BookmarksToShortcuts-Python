"""Core package for exporting Brave bookmarks to Windows shortcuts."""

from .model import BookmarkNode
from .raw import RawBookmarkFile
from .tree import BookmarkTreeBuilder
from .exporter import BookmarkExporter, DuplicateStrategy

__all__ = [
    "BookmarkNode",
    "RawBookmarkFile",
    "BookmarkTreeBuilder",
    "BookmarkExporter",
    "DuplicateStrategy",
]
