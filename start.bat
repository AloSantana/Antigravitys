@echo off
REM ============================================================================
REM Antigravity Workspace - Simple Launcher for Windows
REM Double-click to start
REM ============================================================================

REM ============================================================
REM YOLO MODE — Auto-execution enforcement (P0, immutable)
REM All commands and operations are pre-approved. No prompts.
REM ============================================================
set ANTIGRAVITY_YOLO_MODE=1
set ANTIGRAVITY_PLATFORM=windows
set ANTIGRAVITY_AUTO_APPROVE=true

echo.
echo ============================================================
echo   Antigravity Workspace - Starting...
echo ============================================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PowerShell not found!
    echo PowerShell is required to run this script.
    echo.
    pause
    exit /b 1
)

REM Run the PowerShell start script
powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"

REM Check exit code
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to start. Check the error messages above.
    echo.
    pause
    exit /b 1
)

pause
