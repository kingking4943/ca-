@echo off
REM Script di avvio rapido per Gestionale Gitemania (Windows)
REM Sviluppato da TechExpresso

echo ========================================
echo   GESTIONALE GITEMANIA - TECHEXPRESSO
echo   Avvio Applicazione Desktop
echo ========================================

REM Controlla Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trovato. Installa Python 3.8+ e riprova.
    pause
    exit /b 1
)

REM Mostra versione Python
echo 🐍 Python versione:
python --version

REM Controlla virtual environment
if not defined VIRTUAL_ENV (
    echo ⚠️  Non sei in un virtual environment.
    echo 💡 Consiglio: crea un venv con 'python -m venv venv'
)

REM Controlla dipendenze
echo 📦 Controllo dipendenze...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ❌ tkinter non disponibile. Reinstalla Python con supporto tkinter.
    pause
    exit /b 1
)

REM Installa dipendenze se requirements.txt esiste
if exist requirements.txt (
    echo 📥 Installazione dipendenze...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Errore installazione dipendenze.
        pause
        exit /b 1
    )
) else (
    echo ⚠️  File requirements.txt non trovato.
)

REM Controlla file principale
if not exist gestionale_gitemania.py (
    echo ❌ File gestionale_gitemania.py non trovato.
    pause
    exit /b 1
)

REM Crea cartella exports se non esiste
if not exist exports mkdir exports

echo 🚀 Avvio Gestionale Gitemania...
echo.

REM Avvia applicazione
python gestionale_gitemania.py

REM Cattura codice di uscita
set exit_code=%errorlevel%

echo.
if %exit_code% equ 0 (
    echo ✅ Applicazione chiusa correttamente.
) else (
    echo ❌ Applicazione terminata con errore (codice: %exit_code%).
)

echo 👋 Grazie per aver utilizzato Gestionale Gitemania!
echo 💼 Sviluppato da TechExpresso - www.techexpresso.it

pause
