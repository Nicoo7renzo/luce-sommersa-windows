@echo off
setlocal
cd /d "%~dp0"
title Luce Sommersa - creazione EXE Windows

echo.
echo ============================================
echo       LUCE SOMMERSA - BUILD WINDOWS
echo ============================================
echo.
echo Questo script prepara un eseguibile Windows.
echo Serve una connessione Internet al primo avvio.
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo ERRORE: Python non trovato.
    echo Installa Python 3.11 o 3.12 da https://www.python.org/downloads/windows/
    echo Durante l'installazione seleziona "Add python.exe to PATH".
    pause
    exit /b 1
)

echo [1/4] Aggiornamento pip...
py -m pip install --upgrade pip
if errorlevel 1 goto errore

echo.
echo [2/4] Installazione dipendenze...
py -m pip install -r requirements.txt
if errorlevel 1 goto errore

echo.
echo [3/4] Creazione dell'eseguibile...
py -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name LuceSommersa ^
  --add-data "luce_sommersa_assets;luce_sommersa_assets" ^
  --collect-all pygame ^
  luce_sommersa.py
if errorlevel 1 goto errore

echo.
echo [4/4] Completato!
echo L'eseguibile si trova in:
echo %CD%\dist\LuceSommersa.exe
echo.
echo Copia LuceSommersa.exe dove vuoi. Puoi lasciare la cartella
echo build e il file .spec: non servono per giocare.
pause
exit /b 0

:errore
echo.
echo BUILD NON RIUSCITA. Leggi l'errore mostrato qui sopra.
pause
exit /b 1
