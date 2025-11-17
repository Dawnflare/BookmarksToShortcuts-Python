# Bookmarks to Shortcuts (Python)

This repository contains a lightweight implementation of the Phase 1 deliverables from the PRD: a reusable Python
library that can read Brave bookmark files and export them to Windows `.url` shortcuts.

## Features
- Load Brave's `Bookmarks` JSON file via `RawBookmarkFile`.
- Convert the JSON hierarchy to strongly typed `BookmarkNode` objects with `BookmarkTreeBuilder`.
- Export folders/bookmarks to a mirrored directory structure with `BookmarkExporter`.
- Safe filename sanitization and duplicate-handling strategies (`unique`, `skip`, `overwrite`).
- Minimal CLI harness: `python -m bookmarks_to_shortcuts.cli <Bookmarks path> <output dir>`.

## Development

Run the test suite with:

```bash
pytest
```
