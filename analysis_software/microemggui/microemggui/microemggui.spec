# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for microemggui.

This spec will run `pyside6-rcc` to generate the icons.py resource module
from the Qt resource file before PyInstaller collects sources.

Usage:
    cd analysis_software/microemggui/microemggui
    poetry run pyinstaller --workpath ../../../build/microemggui --distpath ../../../dist/microemggui microemggui.spec
Adjust datas/hiddenimports as required for your environment.
"""

import os
import sys
import subprocess
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

# Paths
HERE = os.getcwd()
PACKAGE_ROOT = HERE

# Verify we're in the microemggui package directory
required_items = ["main.py", "icons", "styles", "docs"]
if not all(os.path.exists(os.path.join(PACKAGE_ROOT, item)) for item in required_items):
    raise RuntimeError(
        f"microemggui.spec must be run from the microemggui package directory. "
        f"Expected to find {required_items} in {PACKAGE_ROOT}"
    )

QRC_PATH = os.path.join(PACKAGE_ROOT, "icons", "icons.qrc")
ICONS_PY = os.path.join(PACKAGE_ROOT, "icons", "icons.py")

# Generate icons.py from icons.qrc (best-effort; non-fatal if command missing)
try:
    subprocess.run(["pyside6-rcc", QRC_PATH, "-o", ICONS_PY], check=False)
except Exception:
    # If pyside6-rcc isn't available in PATH, PyInstaller will still proceed;
    # ensure you run the rcc command manually before building if needed.
    pass

# Entry script
ENTRY_SCRIPT = os.path.join(PACKAGE_ROOT, "main.py")

# Data files to include (source, destination-relative-to-app)
datas = [
    (os.path.join(PACKAGE_ROOT, "styles", "style.qss"), "microemggui/styles"),
    (os.path.join(PACKAGE_ROOT, "docs", "microemg_help_guide.pdf"), "microemggui/docs"),
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
