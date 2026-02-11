@echo off
setlocal enabledelayedexpansion

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

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage

set "BOOKMARKS=%~1"
set "OUTPUT_DIR=%~2"
shift
shift

python -m bookmarks_to_shortcuts.cli "%BOOKMARKS%" "%OUTPUT_DIR%" %*
if errorlevel 1 goto :end

echo.
echo Export complete.

goto :end

:usage
echo Usage: %~nx0 "path\to\Brave\Bookmarks" "path\to\output\folder" [additional options]
echo Example: %~nx0 "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Bookmarks" "D:\Exports" --include-roots bookmark_bar other --duplicate-strategy skip
goto :end

:end
endlocal
