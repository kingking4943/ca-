#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup per compilazione Gestionale Gitemania PORTABLE
Crea file .exe standalone con tutte le dipendenze embedded
Sviluppato da TechExpresso
"""

from setuptools import setup, find_packages
import os
import sys
import subprocess

# Versione applicazione
VERSION = "1.0.0"

# Dipendenze per PyInstaller - Versione Portable
HIDDEN_IMPORTS = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'PIL',
    'PIL._tkinter_finder',
    'woocommerce',
    'cryptography',
    'matplotlib',
    'matplotlib.backends.backend_tkagg',
    'pandas',
    'openpyxl',
    'docx',
    'flask',
    'schedule',
    'apscheduler',
    'qrcode',
    'sqlite3',
    'json',
    'threading',
    'datetime',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'ttkthemes',
    'ttkbootstrap', # <-- AGGIUNTO PER LA NUOVA GRAFICA
]

# Moduli da escludere per ridurre dimensioni
EXCLUDED_MODULES = [
    'test',
    'tests',
    'unittest',
    'pydoc',
    'doctest',
    'tkinter.test',
    'email.test',
    'sqlite3.test',
]

# File da includere
DATA_FILES = [
    ('', ['config.py', 'database_manager.py']),
    ('', ['*.py']),
]

def create_portable_spec_file():
    """Crea file .spec per PyInstaller Portable"""
    
    # Crea icona se non esiste
    create_icon_if_needed()
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
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
    hiddenimports={HIDDEN_IMPORTS},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes={EXCLUDED_MODULES},
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
'''
    
    with open('gestionale_portable.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("📋 File .spec portable creato: gestionale_portable.spec")

def create_icon_if_needed():
    """Crea icona TechExpresso se non esiste"""
    if not os.path.exists('assets'):
        os.makedirs('assets', exist_ok=True)
        
    icon_path = 'assets/icon.ico'
    if not os.path.exists(icon_path):
        print("🎨 Creazione icona TechExpresso...")
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Crea icona semplice 256x256
            img = Image.new('RGBA', (256, 256), color=(51, 122, 183, 255))  # Blu TechExpresso
            draw = ImageDraw.Draw(img)
            
            # Disegna simbolo ingranaggio stilizzato
            center = 128
            radius = 80
            
            # Ingranaggio esterno
            for i in range(8):
                angle = i * 45
                x1 = center + radius * 0.7 * (1 if i % 2 == 0 else 0.9)
                y1 = center + radius * 0.7 * (1 if i % 2 == 0 else 0.9)
                draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                           fill=(255, 255, 255, 255), outline=(51, 122, 183, 255), width=4)
            
            # Cerchio interno
            inner_radius = 30
            draw.ellipse([center-inner_radius, center-inner_radius, 
                         center+inner_radius, center+inner_radius], 
                        fill=(51, 122, 183, 255))
            
            # Salva come ICO
            img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"✅ Icona creata: {icon_path}")
            
        except ImportError:
            print("⚠️ Pillow non disponibile per creare icona")
        except Exception as e:
            print(f"⚠️ Errore creazione icona: {e}")

def create_splash_screen():
    """Crea splash screen di avvio"""
    splash_path = 'assets/splash.png'
    if not os.path.exists(splash_path):
        print("🖼️ Creazione splash screen...")
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Crea splash 400x300
            img = Image.new('RGB', (400, 300), color=(240, 248, 255))  # Azzurro chiaro
            draw = ImageDraw.Draw(img)
            
            # Titolo
            try:
                font_large = ImageFont.truetype("arial.ttf", 24)
                font_small = ImageFont.truetype("arial.ttf", 16)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Testi
            draw.text((200, 100), "Gestionale Gitemania", font=font_large, 
                     fill=(51, 122, 183), anchor="mm")
            draw.text((200, 140), "TechExpresso", font=font_small, 
                     fill=(108, 117, 125), anchor="mm")
            draw.text((200, 180), "Caricamento in corso...", font=font_small, 
                     fill=(108, 117, 125), anchor="mm")
            
            # Barra di caricamento stilizzata
            bar_width = 200
            bar_height = 6
            bar_x = (400 - bar_width) // 2
            bar_y = 220
            
            draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], 
                         fill=(51, 122, 183, 100), outline=(51, 122, 183))
            
            img.save(splash_path, format='PNG')
            print(f"✅ Splash screen creato: {splash_path}")
            
        except Exception as e:
            print(f"⚠️ Errore creazione splash: {e}")

def create_version_info():
    """Crea file informazioni versione portable"""
    version_info = f'''# UTF-8
#
# File di informazioni versione generato automaticamente
# Gestionale Gitemania PORTABLE
#
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'TechExpresso'),
           StringStruct(u'FileDescription', u'Gestionale Gitemania PORTABLE - Sistema gestionale standalone per WooCommerce'),
           StringStruct(u'FileVersion', u'{VERSION}'),
           StringStruct(u'InternalName', u'gestionale_gitemania_portable'),
           StringStruct(u'LegalCopyright', u'Copyright © 2025 TechExpresso - Tutti i diritti riservati'),
           StringStruct(u'OriginalFilename', u'GestionaleGitemania.exe'),
           StringStruct(u'ProductName', u'Gestionale Gitemania PORTABLE'),
           StringStruct(u'ProductVersion', u'{VERSION}'),
           StringStruct(u'Comments', u'Applicazione standalone per gestione ordini WooCommerce - Non richiede installazione Python')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    print("📄 File versione portable creato: version_info.txt")

def install_dependencies():
    """Installa dipendenze necessarie per compilazione"""
    print("📦 Installazione dipendenze per compilazione...")
    
    dependencies = [
        'pyinstaller>=5.13.0',
        'auto-py-to-exe>=2.40.0',
        'pillow>=10.0.0',  # Per icone e splash
        'upx-ucl',  # Per compressione (se disponibile)
    ]
    
    for dep in dependencies:
        try:
            print(f"📥 Installazione {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
        except subprocess.CalledProcessError:
            print(f"⚠️ Impossibile installare {dep} - continuando...")
        except Exception as e:
            print(f"⚠️ Errore installazione {dep}: {e}")

def optimize_executable():
    """Ottimizza eseguibile compilato"""
    exe_path = 'dist/GestionaleGitemania.exe'
    
    if not os.path.exists(exe_path):
        print("❌ Eseguibile non trovato per ottimizzazione")
        return False
        
    print("🔧 Ottimizzazione eseguibile...")
    
    # Verifica dimensioni
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"📏 Dimensione eseguibile: {size_mb:.1f} MB")
    
    # Prova compressione UPX se disponibile
    try:
        subprocess.run(['upx', '--check', exe_path], check=True, capture_output=True)
        print("✅ Compressione UPX già applicata")
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            print("🗜️ Applicazione compressione UPX...")
            subprocess.run(['upx', '--best', '--lzma', exe_path], check=True)
            new_size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            reduction = ((size_mb - new_size_mb) / size_mb) * 100
            print(f"✅ Compressione completata: {new_size_mb:.1f} MB (-{reduction:.1f}%)")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ UPX non disponibile - dimensioni non ottimizzate")
    
    return True

def build_portable_executable():
    """Compila applicazione in eseguibile PORTABLE"""
    print("=" * 60)
    print("  COMPILAZIONE GESTIONALE GITEMANIA PORTABLE v1.0.0")
    print("  Sviluppato da TechExpresso")
    print("  File .exe standalone con database SQLite integrato")
    print("=" * 60)
    
    # Installa dipendenze
    install_dependencies()
    
    # Crea file necessari
    create_portable_spec_file()
    create_version_info()
    create_splash_screen()
    
    # Pulisce compilazioni precedenti
    if os.path.exists('dist'):
        import shutil
        shutil.rmtree('dist')
    if os.path.exists('build'):
        import shutil
        shutil.rmtree('build')
        
    print("\n🔨 Compilazione in corso...")
    print("Questo potrebbe richiedere 5-10 minuti per la prima compilazione...")
    
    # Comando PyInstaller per versione portable
    cmd = [
        'pyinstaller',
        'gestionale_portable.spec',
        '--clean',
        '--noconfirm',
        '--log-level=WARN'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if os.path.exists('dist/GestionaleGitemania.exe'):
            print("\n✅ COMPILAZIONE COMPLETATA CON SUCCESSO!")
            
            # Ottimizza eseguibile
            optimize_executable()
            
            # Crea package di distribuzione
            create_distribution_package()
            
            # Test finale
            test_portable_executable()
            
            print("\n" + "=" * 60)
            print("🎉 GESTIONALE GITEMANIA PORTABLE PRONTO!")
            print(f"📁 File eseguibile: dist/GestionaleGitemania.exe")
            print(f"📦 Package completo: dist/GestionaleGitemania_Portable/")
            print("💡 Istruzioni: Doppio click su GestionaleGitemania.exe")
            print("=" * 60)
            
        else:
            print("❌ Eseguibile non trovato dopo compilazione")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERRORE DURANTE LA COMPILAZIONE")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"\n❌ Errore imprevisto: {e}")
        return False
        
    return True

def create_distribution_package():
    """Crea package di distribuzione completo"""
    print("📦 Creazione package di distribuzione...")
    
    dist_dir = 'dist/GestionaleGitemania_Portable'
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    # Copia eseguibile
    import shutil
    if os.path.exists('dist/GestionaleGitemania.exe'):
        shutil.copy2('dist/GestionaleGitemania.exe', dist_dir)
    
    # Crea cartelle necessarie
    for folder in ['data', 'exports', 'logs', 'docs']:
        folder_path = os.path.join(dist_dir, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    
    # Crea file README
    readme_content = """# Gestionale Gitemania PORTABLE

## 🚀 Avvio Rapido
1. Doppio click su `GestionaleGitemania.exe`
2. Al primo avvio si aprirà il wizard di configurazione
3. Inserisci le credenziali WooCommerce
4. Il sistema è pronto!

## 📁 Struttura Cartelle
- `data/` - Database locale e configurazione
- `exports/` - File CSV/DOCX esportati
- `logs/` - File di log dell'applicazione
- `docs/` - Documentazione aggiuntiva

## ⚙️ Configurazione WooCommerce
- URL Negozio: https://tuonegozio.com
- Consumer Key: (dalle impostazioni WooCommerce API)
- Consumer Secret: (dalle impostazioni WooCommerce API)

## 🔧 Caratteristiche
✅ **Standalone** - Non richiede Python installato
✅ **Portable** - Tutti i dati in cartelle locali
✅ **Sicuro** - Credenziali crittografate
✅ **Auto-sync** - Sincronizzazione automatica ordini
✅ **Export** - CSV e DOCX automatici
✅ **Backup** - Backup automatico dati

## 🆘 Supporto
Sviluppato da **TechExpresso**
Per supporto: info@techexpresso.it

## 🔄 Aggiornamenti
Per aggiornare, sostituisci solo il file .exe mantenendo le cartelle dati.
"""
    
    with open(os.path.join(dist_dir, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Copia documentazione se esiste
    if os.path.exists('README.md'):
        shutil.copy2('README.md', os.path.join(dist_dir, 'docs/'))
    
    print(f"✅ Package creato: {dist_dir}")

def test_portable_executable():
    """Test base dell'eseguibile portable"""
    exe_path = 'dist/GestionaleGitemania.exe'
    
    if not os.path.exists(exe_path):
        print("❌ Eseguibile non trovato per test")
        return False
    
    print("🧪 Test eseguibile portable...")
    
    # Test 1: Verifica che sia un PE valido
    try:
        import pefile
        pe = pefile.PE(exe_path)
        print("✅ File PE valido")
    except ImportError:
        print("⚠️ pefile non disponibile - saltando verifica PE")
    except Exception as e:
        print(f"❌ File PE non valido: {e}")
        return False
    
    # Test 2: Verifica dimensioni ragionevoli
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    if size_mb > 200:
        print(f"⚠️ Eseguibile molto grande: {size_mb:.1f} MB")
    else:
        print(f"✅ Dimensioni accettabili: {size_mb:.1f} MB")
    
    # Test 3: Verifica che non sia una console app
    try:
        with open(exe_path, 'rb') as f:
            data = f.read(1024)
            if b'Console' in data:
                print("⚠️ Potrebbe aprire console")
            else:
                print("✅ Applicazione GUI (no console)")
    except:
        pass
    
    print("✅ Test completati")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        success = build_portable_executable()
        sys.exit(0 if success else 1)
    else:
        setup(
            name="gestionale-gitemania-portable",
            version=VERSION,
            description="Gestionale Desktop PORTABLE per Gitemania.com - Standalone con database SQLite",
            author="TechExpresso",
            author_email="info@techexpresso.it",
            packages=find_packages(),
            python_requires=">=3.8",
            install_requires=[
                'tkinter-tooltip>=1.0.0',
                'Pillow>=10.0.0',
                'woocommerce>=3.0.0',
                'requests>=2.31.0',
                'cryptography>=41.0.3',
                'pandas>=2.0.3',
                'openpyxl>=3.1.2',
                'python-docx>=0.8.11',
                'schedule>=1.2.0',
                'apscheduler>=3.10.1',
                'flask>=2.3.2',
                'qrcode>=7.4.2',
                'ttkthemes>=3.2.2',
                'ttkbootstrap>=1.10.1',
            ],
            entry_points={
                'console_scripts': [
                    'gestionale-gitemania=gestionale_gitemania:main',
                ],
            },
            classifiers=[
                "Development Status :: 5 - Production/Stable",
                "Intended Audience :: End Users/Desktop",
                "License :: OSI Approved :: MIT License",
                "Programming Language :: Python :: 3",
                "Operating System :: Microsoft :: Windows",
                "Topic :: Office/Business",
                "Topic :: Office/Business :: Financial",
            ],
        )
