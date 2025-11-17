@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
call "%SCRIPT_DIR%\.venv\Scripts\activate.bat"

python -m bookmarks_to_shortcuts.gui %*

endlocal
