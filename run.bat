@echo off
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python не найден. Установите его с https://www.python.org/downloads/
    echo и при установке отметьте галочку "Add python.exe to PATH".
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Первый запуск: создаю окружение и устанавливаю PyQt6, подождите...
    python -m venv .venv || goto fail
    ".venv\Scripts\python.exe" -m pip install --upgrade pip || goto fail
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto fail
)

".venv\Scripts\python.exe" main.py
if errorlevel 1 pause
exit /b 0

:fail
echo.
echo Не удалось установить PyQt6. Проверьте подключение к интернету и запустите снова.
if exist .venv rmdir /s /q .venv
pause
exit /b 1
