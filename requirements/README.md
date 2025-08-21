# Requirements 文件说明

本文件夹包含了 LifeTrace 项目的所有依赖文件，按功能模块分类：

## 📦 依赖文件列表

### `requirements.txt`
**核心依赖文件**
- 包含 LifeTrace 系统的基础依赖
- 包括 FastAPI、SQLAlchemy、RapidOCR 等核心组件
- 安装命令：`pip install -r requirements.txt`

### `requirements_vector.txt`
**向量数据库依赖**
- 语义搜索和向量数据库功能所需的依赖
- 包括 ChromaDB、sentence-transformers 等
- 安装命令：`pip install -r requirements_vector.txt`

### `requirements_multimodal.txt`
**多模态搜索依赖**
- 多模态搜索功能所需的依赖
- 包括 CLIP 模型相关组件
- 安装命令：`pip install -r requirements_multimodal.txt`

### `requirements_rapidocr.txt`
**RapidOCR 专用依赖**
- RapidOCR 引擎的专用依赖文件
- 优化的 OCR 处理性能
- 安装命令：`pip install -r requirements_rapidocr.txt`

## 🚀 安装指南

### 完整安装（推荐）
```bash
# 安装所有依赖
pip install -r requirements.txt
pip install -r requirements_vector.txt
pip install -r requirements_multimodal.txt
pip install -r requirements_rapidocr.txt
```

### 最小安装
```bash
# 仅安装核心功能
pip install -r requirements.txt
```

### 按需安装
```bash
# 基础功能 + 向量搜索
pip install -r requirements.txt
pip install -r requirements_vector.txt

# 基础功能 + 多模态搜索
pip install -r requirements.txt
pip install -r requirements_multimodal.txt
```

## 📝 注意事项

1. 建议在虚拟环境中安装依赖
2. 某些依赖可能需要特定的系统环境（如 CUDA 支持）
3. 如遇到安装问题，请参考项目主文档的故障排除部分