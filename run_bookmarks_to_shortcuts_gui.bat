@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if not exist ".venv" (
    echo [ERROR] Virtual environment not found.
    echo Please run "setup.bat" first to set up the environment.
    echo.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

start "" pythonw -m bookmarks_to_shortcuts.gui %*

endlocal
