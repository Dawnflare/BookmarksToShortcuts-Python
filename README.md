# Bookmarks to Shortcuts (Python)

This repository contains a lightweight implementation of the Phase 1 deliverables from the PRD: a reusable Python
library that can read Brave bookmark files and export them to Windows `.url` shortcuts. The toolkit has continued to
grow and now includes quality-of-life features for HTML/text exports, combined outputs, and granular folder selection
directly from a GUI.

## Features
- Load Brave's `Bookmarks` JSON file via `RawBookmarkFile`.
- Convert the JSON hierarchy to strongly typed `BookmarkNode` objects with `BookmarkTreeBuilder`.
- Export folders/bookmarks to a mirrored directory structure with `BookmarkExporter`.
- Safe filename sanitization and duplicate-handling strategies (`unique`, `skip`, `overwrite`).
- Choose between preserving the Brave folder hierarchy or combining every bookmark into a single output directory.
- Export your bookmarks as `.url` shortcuts, a standalone HTML document, or a newline-delimited text file.
- Select specific folders to include in the export directly from the Tkinter GUI.
- Minimal CLI harness: `python -m bookmarks_to_shortcuts.cli <Bookmarks path> <output dir>`.

## Usage

### Prerequisites

- Python 3.10 or later (the CLI relies solely on the standard library).
- Access to Brave's `Bookmarks` JSON file. On Windows the file typically lives at
  `%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Bookmarks`. Back up the
  file (or close Brave) before running the exporter to avoid concurrent writes.

### Step-by-step

1. **Install dependencies.** No external packages are required, but it is recommended to
   create and activate a virtual environment before running the CLI (see
   [Manual virtual environment activation](#manual-virtual-environment-activation)).
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

### GUI-only capabilities

The Tkinter front end wraps the same exporter used by the CLI and exposes additional
features that are difficult to express with command-line flags alone:

- **Folder selection.** Browse your Brave hierarchy and include/exclude individual
  folders before exporting. The selection state is preserved across reloads of the
  current `Bookmarks` file.
- **Segregated vs. combined output.** Use the *Bookmark layout* dropdown to control
  whether bookmarks are exported into their Brave folder structure or combined into a
  single directory (useful for quickly scanning many favorites).
- **HTML export.** `Export as HTML` creates a standalone document grouped by folder (or a
  flat list if *Combined* output is selected).
- **Text export.** `Export as text document` creates a newline-delimited list of
  `Name – URL` entries (grouped or flat, matching the structure mode).
- **Shortcut export.** `Export Shortcuts` mirrors the `.url` generation performed by the
  CLI, honoring the folder selection, structure mode, and duplicate-handling strategy.

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
  included roots, duplicate-handling strategy, the "include full path" toggle, folder
  selection, combined output mode, and HTML/text export buttons.

## Manual virtual environment activation

The `.bat` helpers automatically activate the project's virtual environment before launching
Python. If you would rather start the CLI or GUI manually, you can activate the environment
yourself:

```bash
python -m venv .venv
```

Then activate it:

- **PowerShell / Command Prompt (Windows):**

  ```powershell
  .\.venv\Scripts\activate
  ```

- **macOS / Linux shells:**

  ```bash
  source .venv/bin/activate
  ```

Once activated, run either interface directly:

```bash
python -m bookmarks_to_shortcuts.cli "<Bookmarks path>" "<output dir>"
python -m bookmarks_to_shortcuts.gui
```

Deactivate the environment at any time with `deactivate`.

## Development

Run the test suite with:

```bash
pytest
```
