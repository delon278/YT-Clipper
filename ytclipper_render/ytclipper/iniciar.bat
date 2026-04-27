@echo off
chcp 65001 >nul
title YTClipper

echo.
echo ╔════════════════════════════════╗
echo ║       🎬  YTClipper            ║
echo ╚════════════════════════════════╝
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado.
    echo Descarga Python desde https://www.python.org
    echo Asegurate de marcar "Add to PATH" durante la instalacion.
    pause
    exit /b 1
)
echo OK - Python encontrado

echo Instalando dependencias...
pip install --quiet flask yt-dlp
echo OK - Dependencias instaladas

echo.
echo Verificando ffmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo AVISO: ffmpeg no encontrado. Para clipear instala ffmpeg:
    echo   https://ffmpeg.org/download.html
    echo   O con winget: winget install Gyan.FFmpeg
) else (
    echo OK - ffmpeg encontrado
)

echo.
echo Iniciando YTClipper...
echo Abre tu navegador en: http://localhost:5050
echo Presiona Ctrl+C para detener.
echo.

start "" "http://localhost:5050"
cd /d "%~dp0"
python app.py

pause
