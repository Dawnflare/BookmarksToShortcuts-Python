# Bookmarks to Shortcuts (Python)

A powerful, user-friendly tool to export your Brave bookmarks as Windows `.url` shortcuts, HTML files, or text lists. Designed with a modern GUI, it offers granular control over your exports and helps keep your bookmarks organized.

## Key Features

### 🖥️ Modern GUI
- **Intuitive Interface**: Browse your bookmarks, select export options, and monitor progress.
- **Dark/Light Theme**: Toggle between **☀ Light** and **🌙 Dark** modes to match your system preference.
- **Persistent Config**: Remembers your Bookmarks file and Export Destination between sessions.

### 📂 Flexible Export Options
- **Formats**: Export as Windows Shortcuts (`.url`), a standalone HTML document, or a plain text list.
- **Folder Selection**: Choose exactly which folders to export—no need to export everything.
- **Structure Modes**:
    - **Preserve Hierarchy**: Mirrors your Brave folder structure exactly.
    - **Combined**: Flattens all bookmarks into a single folder for easy scanning.
- **Duplicate Handling**: Choose to **Skip**, **Overwrite**, or generate **Unique** filenames for duplicates.

### 🧹 Clean Up & Safety
- **Delete After Export**: Optionally remove exported bookmarks from Brave automatically.
    - **Safety First**: Checks if Brave is running (and blocks execution if it is) to prevent database corruption.
    - **Auto-Backup**: Creates a timestamped `.bak` copy of your Bookmarks file before any deletion.
    - **Smart Pruning**: Automatically removes empty folders left behind after deletion.

## Getting Started

### Prerequisites
- **Python 3.10+** (No external dependencies required).
- **Windows** (Optimized for Windows file paths and `.url` shortcuts).

### Running the Application

1. **Launch the GUI**:
   Double-click `run_bookmarks_to_shortcuts_gui.bat` to verify your environment and launch the application.

   Or run from the command line:
   ```bash
   python -m bookmarks_to_shortcuts.gui
   ```

2. **Select Source & Destination**:
   - **Brave Bookmarks File**: The app attempts to auto-locate this. Typically found at:
     `%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Bookmarks`
   - **Destination Folder**: Where you want your exported files to go.

3. **Customize Options**:
   - Check the **Export Shortcuts**, **HTML**, or **Text** boxes.
   - Toggle **"Include root name"** if you want the top-level folder names in your path.
   - Enable **"Delete exported bookmarks"** if you want to move them out of Brave (Brave must be closed!).

4. **Select Folders**:
   - Expand the tree view and check the boxes for the folders you wish to export.
   - Use **Select all** / **Deselect all** for quick bulk actions.

5. **Export**:
   - Click **Export**. The status box will show the results.

## Development

Run the test suite with:
```bash
pytest
```

---

## Footnote: CLI Usage

For automation or headless environments, a minimal CLI is available:

```bash
python -m bookmarks_to_shortcuts.cli "<path-to-Brave-Bookmarks>" "<output-directory>" [options]
```

### Options
- `--include-roots <root1> <root2> ...`: Limit export to specific roots (e.g., `bookmark_bar`).
- `--include-full-path`: Include root folder name in output path.
- `--duplicate-strategy unique|skip|overwrite`: Handle naming conflicts.
