@echo off
set "root=gpt-3.5-turbo"
set "summaries=%root%\summaries"

:: Ensure the summaries directory exists
if not exist "%summaries%" mkdir "%summaries%"

:: Loop through each subfolder in the root directory
for /d %%D in ("%root%\*") do (
    :: Check if summary.txt exists in the current subfolder
    if exist "%%D\summary.txt" (
        :: Get the folder name
        set "folder_name=%%~nD"
        :: Copy summary.txt to summaries with the folder name
        copy "%%D\summary.txt" "%summaries%\%folder_name%.txt" >nul
    )
)

echo Summaries collected in "%summaries%"