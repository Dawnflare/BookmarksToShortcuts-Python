"""Utilities for loading Brave bookmark files."""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


@dataclass
class RawBookmarkFile:
    """Represents the JSON structure persisted by Brave."""

    source_path: Path
    data: Dict[str, Any]

    @classmethod
    def load(cls, path: str | Path) -> "RawBookmarkFile":
        json_path = Path(path)
        with json_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls(source_path=json_path, data=data)

    def roots(self) -> Dict[str, Any]:
        return self.data.get("roots", {})

    def backup(self) -> Path:
        """Create a timestamped backup of the bookmarks file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.source_path.with_suffix(f".{timestamp}.bak")
        shutil.copy2(self.source_path, backup_path)
        return backup_path

    def save(self) -> None:
        """Write the current data back to the source file."""
        with self.source_path.open("w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=3)

