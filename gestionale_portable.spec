# -*- mode: python ; coding: utf-8 -*-
# Gestionale Gitemania PORTABLE - PyInstaller Spec
# Sviluppato da TechExpresso

import sys
import os

block_cipher = None

# Analisi applicazione
a = Analysis(
    ['gestionale_gitemania.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('database_manager.py', '.'),
        ('woocommerce_api.py', '.'),
        ('export_manager.py', '.'),
        ('gui_components.py', '.'),
    ],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 'PIL', 'PIL._tkinter_finder', 'woocommerce', 'cryptography', 'matplotlib', 'matplotlib.backends.backend_tkagg', 'pandas', 'openpyxl', 'docx', 'flask', 'schedule', 'apscheduler', 'qrcode', 'sqlite3', 'json', 'threading', 'datetime', 'requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna', 'ttkthemes', 'ttkbootstrap'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test', 'tests', 'unittest', 'pydoc', 'doctest', 'tkinter.test', 'email.test', 'sqlite3.test'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filtra file non necessari per ridurre dimensioni
a.datas = [x for x in a.datas if not any(ex in x[0] for ex in ['test', '__pycache__', '.pyc'])]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GestionaleGitemania',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compressione UPX per ridurre dimensioni
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Nasconde console per GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
    version_file='version_info.txt' if os.path.exists('version_info.txt') else None,
    # Splash screen durante caricamento
    splash=Splash('assets/splash.png',
                  binaries=a.binaries,
                  datas=a.datas,
                  text_pos=None,
                  text_size=12,
                  minify_script=True,
                  always_on_top=True) if os.path.exists('assets/splash.png') else None
)
