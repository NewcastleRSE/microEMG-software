# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for microemggui.

This spec will run `pyside6-rcc` to generate the icons.py resource module
from the Qt resource file before PyInstaller collects sources.

Usage:
    poetry run pyinstaller microemggui.spec
from the repository's root directory.

Adjust datas/hiddenimports as required for your environment.
"""

import os
import subprocess
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

# Paths
HERE = os.getcwd()
QRC_PATH = os.path.join("analysis_software", "microemggui", "microemggui", "icons", "icons.qrc")
ICONS_PY = os.path.join("analysis_software", "microemggui", "microemggui", "icons", "icons.py")

# Generate icons.py from icons.qrc (best-effort; non-fatal if command missing)
try:
    subprocess.run(["pyside6-rcc", QRC_PATH, "-o", ICONS_PY], check=False)
except Exception:
    # If pyside6-rcc isn't available in PATH, PyInstaller will still proceed;
    # ensure you run the rcc command manually before building if needed.
    pass

# Entry script
ENTRY_SCRIPT = os.path.join("gui_dev", "gui_dev_main.py")

# Data files to include (source, destination-relative-to-app)
datas = [
    (os.path.join("analysis_software", "microemggui", "microemggui", "styles", "style.qss"), "microemggui/styles"),
    (os.path.join("analysis_software", "microemggui", "microemggui", "docs", "microemg_help_guide.pdf"), "microemggui/docs"),
    (os.path.join("recordings", "64-channel", "Stuart_E2", "raw"), "recordings/64-channel/Stuart_E2/raw"),
]

# Include generated icons.py if present
if os.path.exists(ICONS_PY):
    datas.append((ICONS_PY, "microemggui/icons"))

# Collect any hidden imports PyInstaller may miss for Qt; this is a safe default
hiddenimports = collect_submodules('PySide6')

# Add matplotlib backends that PyInstaller doesn't auto-discover
hiddenimports.extend([
    'matplotlib.backends.backend_svg',
    'matplotlib.backends.backend_agg',
    'matplotlib.backends.backend_pdf',
])

a = Analysis(
    [ENTRY_SCRIPT],
    pathex=[HERE],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='microemggui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=False, name='microemggui')
