---



\# Brave Bookmark Exporter – Product Requirements Document (Python Version)



\## 1. Overview



\### 1.1 Product Name (Working)



\*\*Brave Bookmark Exporter\*\*



\### 1.2 Summary



Brave Bookmark Exporter is a Windows 11 desktop application that reads Brave browser bookmarks and exports them as standard Windows Internet Shortcut files (`.url`) into a user-selected folder. The application preserves the bookmark folder hierarchy by mirroring it as a directory structure under the export root.



The app is intended for users who want to:



\* Back up their bookmarks as discrete files.

\* Organize bookmarks as regular files/folders in Explorer.

\* Use bookmarks across tools and workflows that rely on filesystem access.



\### 1.3 Target Platform \& Tech Stack



\* \*\*OS:\*\* Windows 11 (64-bit)

\* \*\*Runtime:\*\* Python 3.11+ (CPython)

\* \*\*Language:\*\* Python

\* \*\*UI Framework:\*\* Qt for Python (PySide6)

\* \*\*Packaging:\*\* Standalone Windows executable using PyInstaller (or similar)



---



\## 2. Goals \& Non-Goals



\### 2.1 Goals



1\. \*\*Export Brave bookmarks into `.url` files\*\*



&nbsp;  \* Each bookmark becomes a Windows Internet Shortcut (`.url`) file.

&nbsp;  \* Each shortcut contains a valid URL that opens in the default browser.



2\. \*\*Preserve bookmark folder structure\*\*



&nbsp;  \* Bookmark folders map to real directories.

&nbsp;  \* Nested bookmark folders are exported as nested directories under the chosen output folder.



3\. \*\*Flexible export scope\*\*



&nbsp;  \* Export \*\*all bookmarks\*\* for a selected Brave profile.

&nbsp;  \* Export \*\*specific bookmark folders\*\*.

&nbsp;  \* Export \*\*individual bookmarks\*\*.



4\. \*\*Safe, non-destructive behavior\*\*



&nbsp;  \* Read-only access to Brave data.

&nbsp;  \* Never modifies or deletes any files inside Brave’s profile directories.



5\. \*\*Usable GUI for non-technical users\*\*



&nbsp;  \* Simple, understandable interface:



&nbsp;    \* Select profile.

&nbsp;    \* View bookmarks tree.

&nbsp;    \* Select export target(s).

&nbsp;    \* Choose output folder.

&nbsp;    \* Run export with feedback and status.



6\. \*\*Robust export behavior\*\*



&nbsp;  \* Handle:



&nbsp;    \* Large numbers of bookmarks.

&nbsp;    \* Invalid filenames.

&nbsp;    \* Duplicate names.

&nbsp;    \* Long paths (with graceful degradation).



\### 2.2 Non-Goals (for v1)



\* Synchronizing exported shortcuts back into Brave.

\* Bi-directional sync between bookmarks and filesystem.

\* Editing bookmarks inside the app.

\* Exporting favicons or setting custom icons on `.url` files.

\* Supporting non-Brave browsers (Chrome, Edge, etc.) in v1.

\* Providing cloud sync or online backup.

\* Providing a CLI by default (CLI is a possible future enhancement).



---



\## 3. Users \& Use Cases



\### 3.1 Primary User Personas



1\. \*\*Power User / Knowledge Worker\*\*

2\. \*\*Backup-Focused User\*\*

3\. \*\*Automation-Oriented User (Secondary)\*\*



(Same descriptions as original PRD – intent unchanged.)



\### 3.2 Key Use Cases



1\. \*\*Export all bookmarks from Brave\*\*

2\. \*\*Export a specific bookmark folder\*\*

3\. \*\*Export a small curated set of bookmarks\*\*

4\. \*\*Repeat exports\*\* with overwrite / skip / unique-name options.



(Behavior identical to original PRD.)



---



\## 4. Functional Requirements



\### 4.1 Profile Detection \& Selection



\*\*FR-1\*\*: The application shall detect the default Brave user data directory using known standard paths for Windows (e.g., `LOCALAPPDATA\\BraveSoftware\\Brave-Browser\\User Data`).



\*\*FR-2\*\*: The application shall scan for existing Brave profiles, including at least:



\* `Default`

\* `Profile 1`

\* `Profile 2`

\* Any additional profile directories following Brave’s naming pattern.



\*\*FR-3\*\*: For each profile directory, the application shall check if a `Bookmarks` file exists.



\*\*FR-4\*\*: The application shall present the list of profiles with:



\* Human-readable display name (e.g., \*Default\*, \*Profile 1\*).

\* Internally tracked profile path.



\*\*FR-5\*\*: The user shall be able to manually specify a custom Brave profile root path if automatic detection fails (e.g., portable Brave installs), using a “Browse…” dialog.



---



\### 4.2 Bookmark File Handling



\*\*FR-6\*\*: The app shall read Brave’s `Bookmarks` file as JSON (using Python’s `json` module or equivalent).



\*\*FR-7\*\*: To avoid file locking and concurrency issues, the application \*\*should\*\*:



\* Copy the `Bookmarks` file to a temporary location.

\* Parse the copy instead of reading the file in-place.



\*\*FR-8\*\*: If the `Bookmarks` file cannot be read or parsed:



\* The app shall display a clear error message.

\* No export operation shall proceed.



---



\### 4.3 Bookmark Tree Parsing



\*\*FR-9\*\*: The application shall parse the `Bookmarks` JSON into an internal tree representation that includes:



\* Folder nodes.

\* Bookmark (URL) nodes.

\* Root containers (`bookmark\_bar`, `other`, `mobile`).



\*\*FR-10\*\*: Each parsed node shall have:



\* A name.

\* A type (folder or bookmark).

\* A stable identifier (copied from Brave’s `id`).

\* A reference to its parent folder (except root containers).

\* A `RootKind` that indicates the top-level root it belongs to:



&nbsp; \* Bookmark Bar

&nbsp; \* Other Bookmarks

&nbsp; \* Mobile Bookmarks

&nbsp; \* Unknown (for any non-standard roots)



\*\*FR-11\*\*: The internal model shall maintain the original order of children as specified by Brave.



---



\### 4.4 UI: Bookmark Tree Visualization \& Selection



\*\*FR-12\*\*: The main window shall display a tree view (Qt `QTreeView` or `QTreeWidget`) that represents the bookmark folder structure, including all roots.



\*\*FR-13\*\*: Folder nodes shall be visually distinguishable (e.g., folder icon) from bookmark nodes (e.g., link icon).



\*\*FR-14\*\*: The TreeView shall support:



\* Expanding/collapsing folders.

\* Selecting nodes for export (via checkboxes).



\*\*FR-15\*\*: The TreeView selection mechanism shall support:



\* Selecting entire folders for export.

\* Selecting individual bookmarks for export.

\* Configurable behavior: selecting a folder can optionally imply all children.



\*\*FR-16\*\*: There shall be an “Export scope” control:



\* Option A: Export all bookmarks in the profile.

\* Option B: Export only selected folders/bookmarks.



\*\*FR-17\*\*: If “Export all bookmarks” is chosen, the TreeView selection state does not affect the export, but remains visible.



---



\### 4.5 Output Folder \& Path Mapping



\*\*FR-18\*\*: The user shall be able to select an \*\*Output Root Folder\*\* using a standard Windows folder picker dialog (`QFileDialog`).



\*\*FR-19\*\*: For each folder node being exported, the application shall create a corresponding directory under the output root, preserving the hierarchy.



\*\*FR-20\*\*: The app shall provide a setting:



\* “\[ ] Include full path from top-level root”



&nbsp; \* If enabled: folder paths include top-level roots (`Bookmarks Bar`, `Other Bookmarks`, etc.).

&nbsp; \* If disabled: the selected folder(s) are treated as roots in the exported tree.



\*\*FR-21\*\*: For each bookmark node being exported, the app shall compute:



\* A relative directory path based on its folder ancestors.

\* A filename (without extension) derived from the bookmark title, sanitized.



---



\### 4.6 File Naming, Sanitization \& Duplicates



\*\*FR-22\*\*: Bookmark names must be sanitized to valid Windows filenames:



\* Remove or replace invalid characters: `\\ / : \* ? " < > |`.

\* Trim trailing spaces and periods.

\* Limit length to a configurable maximum (e.g., 120 characters).



\*\*FR-23\*\*: The file extension for all exported bookmarks shall be `.url`.



\*\*FR-24\*\*: If a file with the same path already exists, the app shall support \*\*three\*\* behaviors, controlled via options:



\* \*\*Overwrite\*\*: Replace the existing file.

\* \*\*Skip\*\*: Do not re-export this bookmark.

\* \*\*Create unique name\*\*: Append a suffix like ` (2)`, ` (3)` etc. until an unused filename is found.



\*\*FR-24a\*\*: The user shall be able to choose the behavior via a UI option (e.g., radio buttons).

\*\*Default behavior:\*\* \*\*Create unique name\*\*.



---



\### 4.7 `.url` File Contents



\*\*FR-25\*\*: Each exported bookmark file shall conform to the basic Windows Internet Shortcut INI-like format:



```ini

\[InternetShortcut]

URL=<bookmark\_url>

```



\*\*FR-26\*\*: The app shall write valid UTF-8 text files.



\*\*FR-27\*\*: If the URL is missing or clearly invalid (e.g., empty string), the bookmark shall be skipped and logged as an error for the result summary.



---



\### 4.8 Export Process \& Progress Feedback



\*\*FR-28\*\*: When the user clicks “Export”, the application shall:



\* Validate all required inputs (profile, output folder, options).

\* Build the list of bookmarks to export.

\* Run the export operation on a background worker (e.g., Python `QThread` or `concurrent.futures` thread) to keep the UI responsive.



\*\*FR-29\*\*: The app shall display a progress indicator during export:



\* Progress bar showing percentage complete or `current/total` bookmarks.

\* Status text (e.g., “Exporting bookmark X of Y”).



\*\*FR-30\*\*: On completion, the app shall show a summary:



\* Total bookmarks processed.

\* Total bookmarks successfully exported.

\* Total folders created.

\* Count of skipped items (invalid URL, existing file, etc.).

\* Count of errors.



\*\*FR-31\*\*: The summary shall be viewable in the UI and optionally:



\* Copied to clipboard.

\* Saved as a text log file.



---



\### 4.9 Error Handling \& Reporting



\*\*FR-32\*\*: For file system errors (e.g., permission denied, disk full), the app shall:



\* Log the specific error for that node.

\* Continue with remaining nodes where possible.

\* Indicate clearly in the final summary that not all items were exported.



\*\*FR-33\*\*: For malformed JSON or corrupt `Bookmarks` file:



\* The app shall stop processing and display an error message suggesting:



&nbsp; \* Checking Brave installation.

&nbsp; \* Re-running Brave Sync, etc.



\*\*FR-34\*\*: If the output root path is invalid or not writable:



\* The app shall present a blocking error and prevent export start.



---



\### 4.10 Settings \& Persistence



\*\*FR-35\*\*: The app shall persist user settings to a config file under the user’s `%APPDATA%` directory (e.g., via a simple JSON or INI file), including:



\* Last selected Brave profile.

\* Last used output folder.

\* Export options (include root path, overwrite/skip/unique-name, etc.).

\* Any custom root-folder renaming (see below).



\*\*FR-36\*\*: On startup, the app shall restore settings and pre-select previously used options where possible.



\*\*FR-37\*\*: If a previously selected profile no longer exists, the app should fall back gracefully to the default profile or prompt the user to choose a new one.



---



\### 4.11 Root Folder Naming / Renaming



\*\*FR-38\*\*: The app shall allow the user to \*\*optionally rename\*\* the three main root folders when exporting:



\* `Bookmarks Bar`

\* `Other Bookmarks`

\* `Mobile Bookmarks`



\*\*FR-39\*\*: The UI shall expose simple text fields or a dialog to map:



\* Original root name → Exported root folder name.



\*\*FR-40\*\*: If no custom name is provided, default to Brave’s original root name.



---



\## 5. Non-Functional Requirements



\### 5.1 Performance



\*\*NFR-1\*\*: The app should handle at least:



\* 10,000 bookmarks and folders within ~5–10 seconds of export under typical SSD conditions, assuming a local profile.



\*\*NFR-2\*\*: The UI should remain responsive during export (no blocking of main Qt event loop).



\### 5.2 Reliability



\*\*NFR-3\*\*: Export should be idempotent under “Skip existing” and deterministic under “Overwrite” or “Create unique name”.



\*\*NFR-4\*\*: Partial failures should be tolerated; the app should export what it can and report any failures.



\### 5.3 Security \& Privacy



\*\*NFR-5\*\*: The app shall not transmit any bookmark data off-device.



\*\*NFR-6\*\*: No external network calls are required for v1 (purely local).



\### 5.4 Usability



\*\*NFR-7\*\*: Users should be able to:



\* Run the installer or unpack a zip.

\* Complete a basic “export all bookmarks” workflow within 1–2 minutes on first use.



\*\*NFR-8\*\*: Errors and warnings should be written in clear, non-technical language where possible.



\### 5.5 Maintainability \& Extensibility



\*\*NFR-9\*\*: The core logic (parsing and export) should be separated into a Python package/module, distinct from the Qt UI, enabling:



\* Unit testing (e.g., with `pytest`).

\* Future CLI wrapper or additional UIs (e.g., TUI or web UI).



\*\*NFR-10\*\*: The app should be structured so that supporting other Chromium-based browsers (Chrome, Edge) is straightforward in a future release (e.g., pluggable “browser provider” abstraction).



\*\*NFR-11\*\*: Code style should follow PEP 8 and be type-annotated (PEP 484) where practical.



---



\## 6. Data Model (Conceptual)



\### 6.1 Raw Data Structures (Deserialization Layer)



Modeled as Python dataclasses or plain dicts/lists.



\*\*RawBookmarkFile\*\*



\* `version`: str

\* `checksum`: str

\* `roots`: `RawRoots`

\* `meta\_info`: dict (optional)



\*\*RawRoots\*\*



\* `bookmark\_bar`: `RawFolderNode`

\* `other`: `RawFolderNode`

\* `mobile`: `RawFolderNode`

\* Extra roots map (optional).



\*\*RawNode\*\* (generic node)



\* `id`: str

\* `name`: str

\* `type`: str (`"folder"` or `"url"`)

\* `date\_added`: str

\* `guid`: str (optional)

\* `meta\_info`: dict (optional)

\* `url`: str (for `url` type)

\* `children`: list\[`RawNode`] (for `folder` type)

\* `date\_modified`: str (optional, folders)



\### 6.2 Domain Model (Application Logic)



Represented as Python classes / dataclasses.



\*\*BookmarkNode\*\* (abstract)



\* `id`: str

\* `name`: str

\* `parent`: `BookmarkFolder | None`

\* `node\_type`: enum (`Folder`, `Bookmark`)

\* `root\_kind`: enum (`BookmarkBar`, `Other`, `Mobile`, `Unknown`)

\* Computed properties:



&nbsp; \* `full\_path\_components`: list\[str]

&nbsp; \* `display\_path`: str



\*\*BookmarkFolder\*\* (extends `BookmarkNode`)



\* `node\_type` = `Folder`

\* `children`: list\[`BookmarkNode`]

\* `is\_root\_folder`: bool



\*\*BookmarkItem\*\* (extends `BookmarkNode`)



\* `node\_type` = `Bookmark`

\* `url`: str



\*\*BraveProfileInfo\*\*



\* `display\_name`: str

\* `profile\_id`: str

\* `profile\_path`: str

\* `bookmark\_file\_path`: str

\* `bookmark\_roots`: `BookmarkRootsModel` (loaded on demand)



\*\*BookmarkRootsModel\*\*



\* `bookmark\_bar`: `BookmarkFolder`

\* `other`: `BookmarkFolder`

\* `mobile`: `BookmarkFolder`

\* `all\_roots`: list\[`BookmarkFolder`]



\### 6.3 Export Model



\*\*ExportOptions\*\*



\* `output\_root\_path`: str

\* `scope`: enum (`AllBookmarks`, `SelectedNodes`)

\* `include\_root\_path`: bool

\* `duplicate\_strategy`: enum (`Overwrite`, `Skip`, `UniqueName`)

\* `max\_file\_name\_length`: int (e.g., 120)

\* `sanitize\_file\_names`: bool

\* `root\_name\_overrides`: dict\[root\_kind → str] (optional)



\*\*ExportTarget\*\*



\* `node`: `BookmarkItem`

\* `relative\_folder\_path\_components`: list\[str]

\* `file\_name\_without\_extension`: str

\* `resolved\_full\_path`: str (final `.url` path after duplicate handling)



\*\*ExportResult\*\*



\* `total\_nodes\_considered`: int

\* `total\_bookmarks\_exported`: int

\* `total\_folders\_created`: int

\* `skipped\_invalid\_url`: int

\* `skipped\_existing`: int

\* `errors`: list\[`ExportError`]



\*\*ExportError\*\*



\* `node\_name`: str

\* `url`: str

\* `reason`: str

\* `exception\_details`: str (optional)



---



\## 7. UX / UI Flows (Qt/PySide6)



\### 7.1 Main Screen Layout (Conceptual)



1\. \*\*Header area\*\*



&nbsp;  \* App title: “Brave Bookmark Exporter”.

&nbsp;  \* Profile selector:



&nbsp;    \* `QComboBox` listing detected Brave profiles by display name.

&nbsp;    \* “Browse…” (`QPushButton`) for custom profile path.

&nbsp;  \* “Reload Bookmarks” button.



2\. \*\*Left pane: Bookmark Tree\*\*



&nbsp;  \* `QTreeWidget` / `QTreeView` showing:



&nbsp;    \* `Bookmarks Bar`

&nbsp;    \* `Other Bookmarks`

&nbsp;    \* `Mobile Bookmarks`

&nbsp;  \* Checkboxes on each node:



&nbsp;    \* Folder or bookmark can be marked for export.

&nbsp;  \* Optional search/filter box (`QLineEdit`) above TreeView.



3\. \*\*Right pane: Export Settings\*\*



&nbsp;  \* Output folder:



&nbsp;    \* `QLineEdit` for selected path.

&nbsp;    \* “Browse…” button.

&nbsp;  \* Export scope:



&nbsp;    \* Radio buttons:



&nbsp;      \* “Export all bookmarks in this profile”

&nbsp;      \* “Export only selected folders/bookmarks”

&nbsp;  \* Options:



&nbsp;    \* “\[ ] Include full path from top-level root”

&nbsp;    \* Duplicate handling: radio buttons for:



&nbsp;      \* Overwrite existing files

&nbsp;      \* Skip existing files

&nbsp;      \* Create unique names (default)

&nbsp;    \* Root-name overrides UI (e.g., button to open a small dialog or inline text fields per root).

&nbsp;  \* Buttons:



&nbsp;    \* “Export Shortcuts”

&nbsp;    \* “Open Output Folder” (enabled after an export)



4\. \*\*Bottom area: Status \& Log\*\*



&nbsp;  \* `QProgressBar` (hidden when idle).

&nbsp;  \* Status text label (e.g., “Ready”, “Exporting 30 of 200…”).

&nbsp;  \* Collapsible “Details” area for export summary and recent messages/errors (e.g., `QTextEdit` in read-only mode).



---



\## 8. System Design \& Architecture (Python)



\### 8.1 High-Level Modules



1\. \*\*`profiles.py` – BraveProfileDetector\*\*



&nbsp;  \* Finds Brave user data directories.

&nbsp;  \* Enumerates profile folders.

&nbsp;  \* Returns `BraveProfileInfo` instances.



2\. \*\*`loader.py` – BookmarkFileLoader\*\*



&nbsp;  \* Given a `BraveProfileInfo`, locates and copies the `Bookmarks` file to a temporary path.

&nbsp;  \* Reads JSON and deserializes into `RawBookmarkFile`.



3\. \*\*`tree\_builder.py` – BookmarkTreeBuilder\*\*



&nbsp;  \* Transforms `RawBookmarkFile` → `BookmarkRootsModel`:



&nbsp;    \* Instantiates `BookmarkFolder` and `BookmarkItem`.

&nbsp;    \* Sets parent-child relationships.

&nbsp;    \* Assigns `RootKind`.



4\. \*\*`exporter.py` – BookmarkExporter\*\*



&nbsp;  \* Given:



&nbsp;    \* `BookmarkRootsModel`

&nbsp;    \* A set of selected nodes and/or scope == `AllBookmarks`

&nbsp;    \* `ExportOptions`

&nbsp;  \* Produces:



&nbsp;    \* On disk: directories and `.url` files.

&nbsp;    \* In memory: `ExportResult`.



5\. \*\*`settings.py` – SettingsManager\*\*



&nbsp;  \* Persist and load configuration (JSON or INI) under `%APPDATA%`.



6\. \*\*`ui/` package – Qt UI Layer\*\*



&nbsp;  \* `main\_window.py` – MainWindow class.

&nbsp;  \* `viewmodels.py` – View models / adapters.

&nbsp;  \* Connects UI events to core functions via signals/slots.



\### 8.2 Threading / Concurrency



\* \*\*UI Thread\*\*:



&nbsp; \* Runs the Qt event loop.

\* \*\*Worker Thread\*\*:



&nbsp; \* Export process (and possibly bookmark loading) runs via `QThread` or `QThreadPool` with `QRunnable`, or `concurrent.futures.ThreadPoolExecutor` integrated with Qt signals.

\* Progress and completion events are signalled back to the main thread safely via Qt signals/slots.



---



\## 9. Risks \& Mitigations



\*\*Risk 1\*\*: Brave data file format changes in future.

\*Mitigation\*: Keep deserialization tolerant, log mismatches clearly.



\*\*Risk 2\*\*: Long path issues on systems where long paths are not enabled.

\*Mitigation\*: Limit filename component length; detect and log path-too-long errors; warn in summary.



\*\*Risk 3\*\*: Multiple bookmarks with identical names in the same folder.

\*Mitigation\*: Provide explicit duplicate strategies; default “Create unique name” to avoid data loss.



\*\*Risk 4\*\*: User confusion about “include full path from root” behavior.

\*Mitigation\*: Provide concise tooltip/description and a small preview example.



\*\*Risk 5\*\*: Python runtime / antivirus false positives on packaged EXE.

\*Mitigation\*: Sign installer where possible; document that the app is offline/local; consider distributing both raw `.py` version and packaged EXE.



---



\## 10. Milestones \& Phases



\### Phase 1 – Core Engine (Python Library)



\* Implement:



&nbsp; \* `RawBookmarkFile` deserialization.

&nbsp; \* `BookmarkTreeBuilder`.

&nbsp; \* `BookmarkExporter` with duplicate strategies and root renaming.

\* Minimal CLI or script harness for testing.

\* Unit tests for parsing and export mapping.



\### Phase 2 – Basic Qt UI



\* Implement:



&nbsp; \* Profile detection UI.

&nbsp; \* Bookmark TreeView (read-only).

&nbsp; \* Output path selection.

&nbsp; \* “Export All” button.

\* Wire up export engine; show basic progress.



\### Phase 3 – Full Selection \& Options



\* Add:



&nbsp; \* Tree node checkboxes (folder + bookmark).

&nbsp; \* Export scope options (all vs selected).

&nbsp; \* Include root path toggle.

&nbsp; \* Duplicate-handling options (overwrite/skip/unique-name; default unique-name).

&nbsp; \* Root renaming UI.



\### Phase 4 – Polish \& Packaging



\* Add:



&nbsp; \* Settings persistence.

&nbsp; \* Improved error messages and summary/log file.

&nbsp; \* Application icon and simple About box.

\* Package:



&nbsp; \* Build Windows EXE with PyInstaller.

&nbsp; \* Optionally create an MSI or simple installer.



---



