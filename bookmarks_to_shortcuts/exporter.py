"""Bookmark export engine."""
from __future__ import annotations

import html
import itertools
import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from .model import BookmarkNode

INVALID_CHARS = re.compile(r"[\\/:*?\"<>|]")


class DuplicateStrategy(str, Enum):
    UNIQUE = "unique"
    OVERWRITE = "overwrite"
    SKIP = "skip"


@dataclass
class ExportResult:
    created_files: List[Path]
    skipped: List[Path]


class BookmarkExporter:
    def __init__(
        self,
        output_root: str | Path,
        include_full_path: bool = True,
        duplicate_strategy: DuplicateStrategy = DuplicateStrategy.UNIQUE,
        max_name_length: int = 120,
    ) -> None:
        self.output_root = Path(output_root)
        self.include_full_path = include_full_path
        self.duplicate_strategy = duplicate_strategy
        self.max_name_length = max_name_length

    def export(self, nodes: Iterable[BookmarkNode]) -> ExportResult:
        created: List[Path] = []
        skipped: List[Path] = []
        for node in nodes:
            if not node.is_folder:
                continue
            self._export_folder(node, created, skipped, base_components=[])
        return ExportResult(created_files=created, skipped=skipped)

    def export_html(self, nodes: Iterable[BookmarkNode], output_file: Path | str) -> int:
        """Create a standalone HTML document listing all bookmarks."""

        sections = self._bookmarks_grouped_by_folder(nodes)
        bookmark_count = sum(len(bookmarks) for _, bookmarks in sections)
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self._html_document(sections), encoding="utf-8")
        return bookmark_count

    def export_text(self, nodes: Iterable[BookmarkNode], output_file: Path | str) -> int:
        """Create a newline-delimited list of bookmark URLs."""

        sections = self._bookmarks_grouped_by_folder(nodes)
        bookmark_count = sum(len(bookmarks) for _, bookmarks in sections)
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self._text_document(sections), encoding="utf-8")
        return bookmark_count

    def _export_folder(
        self,
        folder: BookmarkNode,
        created: List[Path],
        skipped: List[Path],
        base_components: List[str],
    ) -> None:
        if not self._folder_contains_bookmarks(folder):
            return
        components = base_components + folder.path_components if self.include_full_path else base_components + [folder.name]
        folder_path = self.output_root.joinpath(*map(self._sanitize, components))
        folder_path.mkdir(parents=True, exist_ok=True)

        for child in folder.children:
            if child.is_folder:
                next_base = base_components if self.include_full_path else base_components + [self._sanitize(folder.name)]
                self._export_folder(child, created, skipped, next_base)
            else:
                target = folder_path / f"{self._sanitize(child.name)}.url"
                final_path = self._handle_duplicates(target)
                if final_path is None:
                    skipped.append(target)
                    continue
                content = self._shortcut_contents(child.url or "")
                final_path.write_text(content, encoding="utf-8")
                created.append(final_path)

    def _handle_duplicates(self, target: Path) -> Path | None:
        if not target.exists():
            return target
        if self.duplicate_strategy == DuplicateStrategy.SKIP:
            return None
        if self.duplicate_strategy == DuplicateStrategy.OVERWRITE:
            return target
        stem = target.stem
        suffix = target.suffix
        for idx in itertools.count(2):
            candidate = target.with_name(f"{stem} ({idx}){suffix}")
            if not candidate.exists():
                return candidate
        raise RuntimeError("Failed to resolve duplicate filename")

    def _sanitize(self, name: str) -> str:
        clean = INVALID_CHARS.sub("_", name).strip().rstrip(".")
        if not clean:
            clean = "bookmark"
        if len(clean) > self.max_name_length:
            clean = clean[: self.max_name_length].rstrip()
        return clean

    @staticmethod
    def _shortcut_contents(url: str) -> str:
        return f"[InternetShortcut]\nURL={url}\n"

    def _folder_contains_bookmarks(self, folder: BookmarkNode) -> bool:
        for child in folder.children:
            if not child.is_folder:
                return True
            if self._folder_contains_bookmarks(child):
                return True
        return False

    def _iter_bookmark_nodes(self, nodes: Iterable[BookmarkNode]) -> Iterable[BookmarkNode]:
        for node in nodes:
            if not node.is_folder and node.url:
                yield node
            for descendant in node.iter_descendants():
                if descendant.is_folder:
                    continue
                if not descendant.url:
                    continue
                yield descendant

    def _bookmarks_grouped_by_folder(
        self, nodes: Iterable[BookmarkNode]
    ) -> List[Tuple[Tuple[str, ...], List[BookmarkNode]]]:
        sections: Dict[Tuple[str, ...], List[BookmarkNode]] = defaultdict(list)
        for bookmark in self._iter_bookmark_nodes(nodes):
            path = tuple(bookmark.path_components[:-1])
            sections[path].append(bookmark)

        ordered_sections: List[Tuple[Tuple[str, ...], List[BookmarkNode]]] = []
        for path in sorted(sections, key=self._section_sort_key):
            ordered_sections.append((path, sorted(sections[path], key=self._bookmark_sort_key)))
        return ordered_sections

    @staticmethod
    def _section_sort_key(path: Sequence[str]) -> Tuple[str, ...]:
        return tuple(part.casefold() for part in path)

    @staticmethod
    def _bookmark_sort_key(bookmark: BookmarkNode) -> Tuple[str, str]:
        name = bookmark.name or bookmark.url or ""
        return (name.casefold(), (bookmark.url or "").casefold())

    @staticmethod
    def _section_label(path: Sequence[str]) -> str:
        if path:
            return " / ".join(path)
        return "Bookmarks"

    def _html_document(
        self, sections: List[Tuple[Tuple[str, ...], List[BookmarkNode]]]
    ) -> str:
        lines = [
            "<!DOCTYPE html>",
            "<html lang=\"en\">",
            "<head>",
            "  <meta charset=\"utf-8\" />",
            "  <title>Bookmarks Export</title>",
            "</head>",
            "<body>",
        ]
        for path, bookmarks in sections:
            section_label = html.escape(self._section_label(path))
            lines.append(f"  <h2>{section_label}</h2>")
            lines.append("  <ul>")
            for bookmark in bookmarks:
                url = html.escape(bookmark.url or "#", quote=True)
                label = html.escape(bookmark.name or bookmark.url or "Bookmark")
                lines.append(f'    <li><a href="{url}">{label}</a></li>')
            lines.append("  </ul>")
        lines.extend(["</body>", "</html>"])
        return "\n".join(lines)

    def _text_document(
        self, sections: List[Tuple[Tuple[str, ...], List[BookmarkNode]]]
    ) -> str:
        section_blocks: List[str] = []
        for path, bookmarks in sections:
            header = self._section_label(path)
            entries = []
            for bookmark in bookmarks:
                name = bookmark.name or bookmark.url or "Bookmark"
                url = bookmark.url or ""
                entries.append(f"{name} - {url}".rstrip())
            section_blocks.append("\n".join([header] + entries))
        return "\n\n".join(section_blocks)
