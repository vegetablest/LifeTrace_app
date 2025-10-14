# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(os.getcwd())

block_cipher = None

a = Analysis(
    ['lifetrace_backend/server.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # 包含配置文件
        ('config/default_config.yaml', 'config'),
        # 包含必要的数据目录结构
        ('lifetrace_backend/*.py', 'lifetrace_backend'),
        # 包含模板文件 - 修复路径配置，包含整个templates目录
        ('lifetrace_backend/templates', 'lifetrace_backend/templates'),
        # 包含静态文件（本地化的 JS 库）
        ('lifetrace_backend/static', 'lifetrace_backend/static'),
    ],
    hiddenimports=[
        'lifetrace_backend.config',
        'lifetrace_backend.utils', 
        'lifetrace_backend.storage',
        'lifetrace_backend.logging_config',
        'lifetrace_backend.simple_heartbeat',
        'lifetrace_backend.app_mapping',
        'lifetrace_backend.models',
        'lifetrace_backend.simple_ocr',
        'lifetrace_backend.vector_service',
        'lifetrace_backend.multimodal_vector_service',
        'lifetrace_backend.rag_service',
        'lifetrace_backend.behavior_tracker',
        'lifetrace_backend.retrieval_service',
        'lifetrace_backend.multimodal_embedding',
        'lifetrace_backend.vector_db',
        'lifetrace_backend.token_usage_logger',
        'lifetrace_backend.processor',
        'lifetrace_backend.file_monitor',
        'lifetrace_backend.consistency_checker',
        'lifetrace_backend.sync_service',
        'fastapi',
        'uvicorn',
        'jinja2',
        'sqlalchemy',
        'pydantic',
        'yaml',
        'numpy',
        'scipy',
        'PIL',
        'imagehash',
        'psutil',
        'watchdog',
        'rapidocr_onnxruntime',
        'onnxruntime',
        'transformers',
        'torch',
        'sentence_transformers',
        'chromadb',
        'chromadb.utils.embedding_functions',
        'chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2',
        'chromadb.utils.embedding_functions.sentence_transformer_ef',
        'chromadb.utils.embedding_functions.open_clip_ef',
        'chromadb.utils.embedding_functions.hugging_face_ef',
        'chromadb.utils.embedding_functions.instructor_ef',
        'chromadb.utils.embedding_functions.cohere_ef',
        'chromadb.utils.embedding_functions.openai_ef',
        'chromadb.utils.embedding_functions.google_palm_ef',
        'chromadb.utils.embedding_functions.ollama_ef',
        'openai',
        'anthropic',
        'requests',
        'aiofiles',
        'python_multipart',
        'starlette',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块
        'mss',  # server不需要截图功能
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
    name='LifeTrace_Server',
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
)