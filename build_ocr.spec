# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(os.getcwd())

block_cipher = None

a = Analysis(
    ['ocr_standalone.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # 包含配置文件
        ('config', 'config'),
        # 包含RapidOCR的完整包
        (r'C:\Users\25048\anaconda3\envs\sword\lib\site-packages\rapidocr_onnxruntime', 'rapidocr_onnxruntime'),
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
        'lifetrace_backend.vector_service',
        'lifetrace_backend.multimodal_vector_service',
        'lifetrace_backend.vector_db',
        'lifetrace_backend.simple_ocr',
        'yaml',
        'numpy',
        'PIL',
        'psutil',
        'rapidocr_onnxruntime',
        'onnxruntime',
        # RapidOCR相关模块
        'rapidocr_onnxruntime.main',
        'rapidocr_onnxruntime.utils',
        'rapidocr_onnxruntime.utils.load_image',
        'rapidocr_onnxruntime.utils.parse_parameters',
        'rapidocr_onnxruntime.utils.vis_res',
        'rapidocr_onnxruntime.utils.infer_engine',
        'rapidocr_onnxruntime.utils.logger',
        'rapidocr_onnxruntime.utils.process_img',
        'rapidocr_onnxruntime.ch_ppocr_det',
        'rapidocr_onnxruntime.ch_ppocr_det.text_detect',
        'rapidocr_onnxruntime.ch_ppocr_det.utils',
        'rapidocr_onnxruntime.ch_ppocr_rec',
        'rapidocr_onnxruntime.ch_ppocr_rec.text_recognize',
        'rapidocr_onnxruntime.ch_ppocr_rec.utils',
        'rapidocr_onnxruntime.ch_ppocr_cls',
        'rapidocr_onnxruntime.ch_ppocr_cls.text_cls',
        'rapidocr_onnxruntime.ch_ppocr_cls.utils',
        'rapidocr_onnxruntime.cal_rec_boxes',
        'rapidocr_onnxruntime.cal_rec_boxes.main',
        # 向量数据库相关（可选）
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
        'requests',
        'sqlalchemy',
        'pydantic',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块
        'mss',  # OCR不需要截图功能
        'fastapi',  # OCR不需要web服务
        'uvicorn',  # OCR不需要web服务
        'jinja2',  # OCR不需要模板引擎
        'aiofiles',  # OCR不需要异步文件操作
        'python_multipart',  # OCR不需要文件上传
        'starlette',  # OCR不需要web框架
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
    name='LifeTrace_OCR',
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