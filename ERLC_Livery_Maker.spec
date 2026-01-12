# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/main_tk.py'],
    pathex=[],
    binaries=[],
    datas=[('config.json', '.'), ('templates', 'templates')],
    hiddenimports=['PIL', 'PIL._imaging', 'PIL._tkinter_finder', 'cv2', 'numpy', 'replicate'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ERLC_Livery_Maker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ERLC_Livery_Maker',
)
