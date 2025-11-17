"""Utilities for loading Brave bookmark files."""
from __future__ import annotations

import json
from dataclasses import dataclass
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
