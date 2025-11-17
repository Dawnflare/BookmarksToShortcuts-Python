"""Bookmark export engine."""
from __future__ import annotations

import itertools
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List

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

    def _export_folder(
        self,
        folder: BookmarkNode,
        created: List[Path],
        skipped: List[Path],
        base_components: List[str],
    ) -> None:
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
