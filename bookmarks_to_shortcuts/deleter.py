"""Delete exported bookmarks from the Brave Bookmarks JSON file."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Set

from .raw import RawBookmarkFile


class BookmarkDeleter:
    """Removes specific bookmarks from a Brave Bookmarks file."""

    def __init__(self, raw: RawBookmarkFile):
        self.raw = raw

    def delete(self, ids_to_delete: Set[str], *, prune_empty_folders: bool = True) -> int:
        """Remove bookmarks with the given IDs and optionally prune empty folders.

        Returns the number of bookmarks actually removed.
        """
        removed = 0
        roots = self.raw.roots()
        for key in list(roots.keys()):
            root_node = roots[key]
            if "children" in root_node:
                removed += self._remove_from_children(
                    root_node, ids_to_delete, prune_empty_folders
                )

        self._update_checksum()
        return removed

    def _remove_from_children(
        self,
        parent: Dict[str, Any],
        ids_to_delete: Set[str],
        prune_empty: bool,
    ) -> int:
        """Walk children, remove matching IDs, optionally prune empty folders."""
        removed = 0
        surviving: List[Dict[str, Any]] = []
        for child in parent.get("children", []):
            child_id = str(child.get("id", ""))
            is_folder = child.get("type") == "folder"

            if is_folder:
                # Recurse into folder first
                removed += self._remove_from_children(child, ids_to_delete, prune_empty)
                # Keep the folder unless it's now empty and pruning is on
                if prune_empty and not child.get("children", []):
                    continue  # drop the empty folder
                surviving.append(child)
            elif child_id in ids_to_delete:
                removed += 1  # drop this bookmark
            else:
                surviving.append(child)

        parent["children"] = surviving
        return removed

    def _update_checksum(self) -> None:
        """Recalculate the checksum field the way Brave/Chromium does."""
        roots = self.raw.roots()
        content = json.dumps(roots, separators=(",", ":"), ensure_ascii=False)
        checksum = hashlib.md5(content.encode("utf-8")).hexdigest()
        self.raw.data["checksum"] = checksum
