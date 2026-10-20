@echo off
setlocal enabledelayedexpansion

set MSG=%*
if "%MSG%"=="" set MSG=Auto-sync: update Sentinel codebase at %DATE% %TIME%

echo [SENTINEL AUTO-PUSH] Staging all changes...
git add -A

git diff --cached --quiet
if %ERRORLEVEL% equ 0 (
    echo [SENTINEL AUTO-PUSH] No new changes to commit.
    exit /b 0
)

echo [SENTINEL AUTO-PUSH] Committing: "%MSG%"...
git commit -m "%MSG%"

echo [SENTINEL AUTO-PUSH] Pushing to origin...
git push origin master

echo [SENTINEL AUTO-PUSH] Successfully pushed all changes!
