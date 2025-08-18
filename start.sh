#!/bin/bash
# Script di avvio rapido per Gestionale Gitemania
# Sviluppato da TechExpresso

echo "========================================"
echo "  GESTIONALE GITEMANIA - TECHEXPRESSO"
echo "  Avvio Applicazione Desktop"
echo "========================================"

# Controlla Python
if ! command -v python &> /dev/null; then
    echo "❌ Python non trovato. Installa Python 3.8+ e riprova."
    exit 1
fi

# Controlla versione Python
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "🐍 Python versione: $python_version"

# Controlla se siamo in un virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Non sei in un virtual environment."
    echo "💡 Consiglio: crea un venv con 'python -m venv venv'"
fi

# Controlla dipendenze
echo "📦 Controllo dipendenze..."
if ! pip show tkinter &> /dev/null && ! python -c "import tkinter" &> /dev/null; then
    echo "❌ tkinter non disponibile. Installa Python con supporto tkinter."
    exit 1
fi

# Installa dipendenze se requirements.txt esiste
if [ -f "requirements.txt" ]; then
    echo "📥 Installazione dipendenze..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Errore installazione dipendenze."
        exit 1
    fi
else
    echo "⚠️  File requirements.txt non trovato."
fi

# Controlla file principale
if [ ! -f "gestionale_gitemania.py" ]; then
    echo "❌ File gestionale_gitemania.py non trovato."
    exit 1
fi

# Crea cartella exports se non esiste
mkdir -p exports

echo "🚀 Avvio Gestionale Gitemania..."
echo ""

# Avvia applicazione
python gestionale_gitemania.py

# Cattura codice di uscita
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ Applicazione chiusa correttamente."
else
    echo "❌ Applicazione terminata con errore (codice: $exit_code)."
fi

echo "👋 Grazie per aver utilizzato Gestionale Gitemania!"
echo "💼 Sviluppato da TechExpresso - www.techexpresso.it"
