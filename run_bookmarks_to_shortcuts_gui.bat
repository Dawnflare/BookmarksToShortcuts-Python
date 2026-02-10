@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
call "%SCRIPT_DIR%\.venv\Scripts\activate.bat"

start "" pythonw -m bookmarks_to_shortcuts.gui %*

endlocal
