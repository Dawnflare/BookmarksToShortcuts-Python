@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ################################################
echo # Bookmarks to Shortcuts - Setup               #
echo ################################################
echo.

:: Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10 or later from https://www.python.org/
    pause
    exit /b 1
)

:: Create virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Created .venv folder.
) else (
    echo Virtual environment already exists.
)

:: Install discovery dependencies (none at runtime, only for dev/testing)
echo Installing development dependencies...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ################################################
echo # Setup complete!                              #
echo ################################################
echo.
echo You can now use:
echo   - run_bookmarks_to_shortcuts_gui.bat (GUI)
echo   - run_bookmarks_to_shortcuts.bat (CLI)
echo.
pause
endlocal
