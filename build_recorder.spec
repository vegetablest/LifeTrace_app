# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(os.getcwd())

block_cipher = None

a = Analysis(
    ['recorder_standalone.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # 包含配置文件
        ('config/default_config.yaml', 'config'),
        # 包含必要的数据目录结构
        ('lifetrace_backend/*.py', 'lifetrace_backend'),
    ],
    hiddenimports=[
        'lifetrace_backend.config',
        'lifetrace_backend.utils', 
        'lifetrace_backend.storage',
        'lifetrace_backend.logging_config',
        'lifetrace_backend.simple_heartbeat',
        'lifetrace_backend.app_mapping',
        'lifetrace_backend.models',
        'mss',
        'PIL',
        'imagehash',
        'psutil',
        'sqlalchemy',
        'pydantic',
        'yaml',
        'watchdog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块
        'torch',
        'torchvision', 
        'transformers',
        'fastapi',
        'uvicorn',
        'opencv-python',
        'rapidocr-onnxruntime',
        'numpy',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LifeTrace_Recorder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径
)