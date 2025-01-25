@echo off
setlocal enabledelayedexpansion
set "root=gpt-4o-2024-08-06"
set "summaries=%root%\summaries"

:: Ensure the summaries directory exists
if not exist "%summaries%" mkdir "%summaries%"

:: Loop through each subfolder in the root directory
for /d %%D in ("%root%\*") do (
    :: Get the folder name
    set "folder_name=%%~nD"

    :: Check if summary.txt exists in the current subfolder
    if exist "%%D\summary.txt" (
        :: Copy summary.txt to summaries folder with the folder name
        copy "%%D\summary.txt" "%summaries%\!folder_name!.txt" >nul
    )
)

echo Summaries collected in "%summaries%"
pause

