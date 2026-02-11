"""Persistent configuration for the Bookmarks to Shortcuts application."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


@dataclass
class AppConfig:
    """User-configurable settings persisted across sessions."""

    bookmarks_path: str = ""
    output_path: str = ""

    @classmethod
    def load(cls) -> "AppConfig":
        """Load config from disk, returning defaults if the file is missing or invalid."""
        if CONFIG_PATH.exists():
            try:
                with CONFIG_PATH.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                return cls(
                    bookmarks_path=data.get("bookmarks_path", ""),
                    output_path=data.get("output_path", ""),
                )
            except Exception:
                pass
        return cls()

    def save(self) -> None:
        """Write the current config to disk."""
        with CONFIG_PATH.open("w", encoding="utf-8") as fh:
            json.dump(asdict(self), fh, indent=2)
