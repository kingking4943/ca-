# Gestionale Gitemania - Repository per Compilazione Windows EXE

**🏭 Servizio di compilazione automatica per ottenere il file .exe Windows**

## 🎯 Come Usare Questo Repository

### 1. Carica i File
- Carica tutti i file del gestionale in questo repository
- Assicurati che ci siano tutti i file .py e requirements.txt

### 2. Avvia Compilazione
- Vai nella tab "Actions"
- Clicca "Run workflow" sul workflow "Compila Gestionale Gitemania Windows EXE"
- Aspetta 5-10 minuti

### 3. Scarica .EXE
- Quando il workflow è completato (✅)
- Scarica l'artifact "GestionaleGitemania-Windows-EXE"
- Estrai il ZIP e trovi il tuo GestionaleGitemania.exe!

## 📋 File Necessari

Questi file devono essere presenti nel repository:

```
gestionale_gitemania/
├── gestionale_gitemania.py
├── config.py  
├── database_manager.py
├── woocommerce_api.py
├── export_manager.py
├── gui_components.py
├── setup.py
├── requirements.txt
├── .github/
│   └── workflows/
│       └── build-windows.yml
└── README.md
```

## 🚀 Funzionalità del Gestionale

- **Integrazione WooCommerce** - Sincronizzazione real-time ordini
- **Database SQLite** - Locale e portable
- **Export automatico** - CSV e DOCX ogni mezzanotte
- **GUI Desktop** - Interfaccia professionale
- **Branding TechExpresso** - Sviluppato da TechExpresso
- **Zero installazioni** - File .exe standalone

## 🛠️ Supporto

Sviluppato da **TechExpresso**
- Email: info@techexpresso.it
- Versione: 1.0.0 PORTABLE

---

**Il sistema compilerà automaticamente il tuo file .exe Windows!** 🎉