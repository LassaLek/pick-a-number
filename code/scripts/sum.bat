@echo off
setlocal enabledelayedexpansion

:: Initialize the summary file
set "output_file=final.txt"
echo Filename - TOTAL: XX CORRECT: XX > "%output_file%"

:: Process all .txt files in the current directory
for %%F in (*.txt) do (
    set "file_name=%%F"
    set "total=0"
    set "correct=0"

    :: Count total lines
    for /f %%L in ('find /c /v "" ^< "%%F"') do set "total=%%L"

    :: Count lines with both "number_yes": true and "answers_yes": true
    for /f "usebackq tokens=*" %%L in ("%%F") do (
        set "line=%%L"
        echo !line! | findstr /i "\"number_yes\": true" >nul && echo !line! | findstr /i "\"answers_yes\": true" >nul
        if !errorlevel! equ 0 (
            set /a correct+=1
        )
    )

    :: Write results to the output file
    echo !file_name! - TOTAL: !total! CORRECT: !correct! >> "%output_file%"
)

:: Notify completion
echo Summary written to %output_file%
pause
