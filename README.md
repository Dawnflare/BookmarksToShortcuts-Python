# Bookmarks to Shortcuts (Python)

This repository contains a lightweight implementation of the Phase 1 deliverables from the PRD: a reusable Python
library that can read Brave bookmark files and export them to Windows `.url` shortcuts.

## Features
- Load Brave's `Bookmarks` JSON file via `RawBookmarkFile`.
- Convert the JSON hierarchy to strongly typed `BookmarkNode` objects with `BookmarkTreeBuilder`.
- Export folders/bookmarks to a mirrored directory structure with `BookmarkExporter`.
- Safe filename sanitization and duplicate-handling strategies (`unique`, `skip`, `overwrite`).
- Minimal CLI harness: `python -m bookmarks_to_shortcuts.cli <Bookmarks path> <output dir>`.

## Usage

### Prerequisites

- Python 3.10 or later (the CLI relies solely on the standard library).
- Access to Brave's `Bookmarks` JSON file. On Windows the file typically lives at
  `%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Bookmarks`. Back up the
  file (or close Brave) before running the exporter to avoid concurrent writes.

### Step-by-step

1. **Install dependencies.** No external packages are required, but it is recommended to
   create and activate a virtual environment before running the CLI.
2. **Run the exporter.** From the repository root execute:

   ```bash
   python -m bookmarks_to_shortcuts.cli "<path-to-Brave-Bookmarks>" "<output-directory>"
   ```

3. **Optional flags.**

   - `--include-roots bookmark_bar other synced mobile` – limit the export to specific
     Brave roots (default is all roots).
   - `--include-full-path` – include the root name in the created directory structure.
   - `--duplicate-strategy unique|skip|overwrite` – choose how duplicate filenames are
     handled. The default (`unique`) appends counters to conflicting names; `skip`
     ignores duplicates and `overwrite` replaces files.

4. **Review the output.** The CLI mirrors the folder hierarchy from Brave into the
   target directory and reports how many shortcuts were created or skipped.

### Tkinter GUI

Prefer a graphical interface on Windows? Launch the GUI with:

```bash
python -m bookmarks_to_shortcuts.gui
```

The window lets you browse for the Bookmarks file and destination folder, toggle which
roots to include, decide whether to include the full path, and choose the duplicate-file
strategy. It displays a summary when the export completes.

### Windows helper scripts

Two helper batch files are included for Windows users:

- `run_bookmarks_to_shortcuts.bat` launches the CLI exporter. Supply the path to the Brave
  `Bookmarks` file and the destination directory as arguments (additional CLI flags are
  optional):

  ```bat
  run_bookmarks_to_shortcuts.bat "C:\\Users\\you\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Bookmarks" "D:\\Exported Shortcuts"
  ```

  Any extra parameters you provide (such as `--include-roots mobile`) are forwarded to the
  Python CLI.

- `run_bookmarks_to_shortcuts_gui.bat` launches a Tkinter-based GUI if you prefer a point-
  and-click workflow. The GUI mirrors the CLI options (bookmarks file, destination folder,
  included roots, duplicate-handling strategy, and the "include full path" toggle).

## Development

Run the test suite with:

```bash
pytest
```
