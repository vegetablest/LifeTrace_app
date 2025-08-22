# LifeTrace 文档中心

本文件夹包含�?LifeTrace 系统的所有用法说明和技术文档，已根据最新代码进行更新�?
## 📚 文档列表

### 核心功能文档

#### 1. [OCR_优化说明.md](./OCR_优化说明.md)
- **内容**: OCR 性能优化方案，PaddleOCR �?RapidOCR 的迁�?- **适用对象**: 开发者、系统管理员
- **更新内容**: 
  - 添加�?LifeTrace 系统集成方式
  - 更新了向量数据库集成信息
  - 修正了使用方法和启动命令

#### 2. [RapidOCR集成说明.md](./RapidOCR集成说明.md)
- **内容**: RapidOCR 引擎集成�?LifeTrace 的详细说�?- **适用对象**: 开发�?- **更新内容**:
  - 添加了向量数据库集成功能
  - 更新了启动方式和程序化使用方�?  - 修正了服务端口号

### 搜索功能文档

#### 3. [multimodal_search_guide.md](./multimodal_search_guide.md)
- **内容**: 多模态搜索功能完整指�?- **适用对象**: 用户、开发�?- **更新内容**:
  - 修正了服务启动命令和端口�?  - 更新�?API 接口地址
  - 保持了最新的功能特性说�?
#### 4. [vector_db_usage.md](./vector_db_usage.md)
- **内容**: 向量数据库使用指�?- **适用对象**: 开发者、高级用�?- **更新内容**:
  - 修正了所�?API 端点的端口号
  - 添加了多模态搜�?API 说明
  - 更新了使用示�?
#### 5. [text_to_image_similarity_usage.md](./text_to_image_similarity_usage.md)
- **内容**: 文本与图像相似度计算程序使用说明
- **适用对象**: 用户、开发�?- **更新内容**:
  - 添加�?Web API 使用方式（推荐）
  - 更新了系统集成信�?  - 保持了命令行使用方法

#### 6. [README_image_similarity.md](./README_image_similarity.md)
- **内容**: 图像相似度计算程序详细说�?- **适用对象**: 开发者、技术用�?- **更新内容**:
  - 添加�?Web API 使用方式
  - 更新了系统集成状�?  - 修正了技术实现说�?
### 前端集成文档

#### 7. [前端集成说明.md](./前端集成说明.md)
- **内容**: React 前端�?LifeTrace 后端的集成说�?- **适用对象**: 前端开发�?- **更新内容**:
  - 修正了后端服务端口号
  - 保持了最新的集成架构说明
  - 更新了功能验证结�?
## 🚀 快速开�?
### 系统启动
```bash
# 启动 LifeTrace 完整服务
python -m lifetrace_backend.server --port 8843
```

### 主要功能
1. **OCR 文字识别**: 自动识别截图中的文字内容
2. **语义搜索**: 基于文本语义的智能搜�?3. **多模态搜�?*: 结合文本和图像的综合搜索
4. **向量数据�?*: 高效的语义相似度计算
5. **Web 界面**: 友好的用户交互界�?
## 📖 使用建议

### 新用�?1. 先阅�?[multimodal_search_guide.md](./multimodal_search_guide.md) 了解核心功能
2. 参�?[前端集成说明.md](./前端集成说明.md) 了解界面使用
3. 查看 [OCR_优化说明.md](./OCR_优化说明.md) 了解性能优化

### 开发�?1. 阅读 [RapidOCR集成说明.md](./RapidOCR集成说明.md) 了解技术架�?2. 参�?[vector_db_usage.md](./vector_db_usage.md) 了解 API 使用
3. 查看 [text_to_image_similarity_usage.md](./text_to_image_similarity_usage.md) 了解相似度计�?
### 高级用户
1. 参�?[README_image_similarity.md](./README_image_similarity.md) 进行深度定制
2. 使用命令行工具进行批量处�?3. 通过 API 集成到其他系�?
## 🔧 技术栈

- **OCR 引擎**: RapidOCR (替代 PaddleOCR)
- **多模态模�?*: CLIP (OpenAI)
- **向量数据�?*: ChromaDB (3个实例：文本向量、多模态文本、多模态图�?
- **后端框架**: FastAPI
- **前端框架**: React + TypeScript
- **数据�?*: SQLite

### 向量数据库架�?
LifeTrace 使用 ChromaDB 作为向量数据库后端，共部署了3个独立的向量数据库实例：

1. **文本向量数据�?* (`lifetrace_ocr`)
   - 存储目录：`vector_db/`
   - 用途：OCR 识别文本的语义搜�?   - 模型：sentence-transformers

2. **多模态文本向量数据库** (`lifetrace_text`)
   - 存储目录：`vector_db_text/`
   - 用途：多模态搜索中的文本嵌�?   - 模型：CLIP 文本编码�?
3. **多模态图像向量数据库** (`lifetrace_image`)
   - 存储目录：`vector_db_image/`
   - 用途：多模态搜索中的图像嵌�?   - 模型：CLIP 图像编码�?
这种分层架构设计确保了不同搜索模式的独立性和性能优化�?
## 📝 更新日志

### 2025-01-19
- �?所有文档已移动�?`doc/` 文件�?- �?根据最新代码更新了所有文档内�?- �?修正了端口号�?API 地址
- �?添加�?Web API 使用方式
- �?更新了系统集成信�?- �?修正了向量数据库技术栈描述（sqlite-vec �?ChromaDB�?- �?添加了向量数据库架构详细说明

## 🤝 贡献

如果您发现文档中的错误或需要补充，请：
1. 检查对应的源代码确认最新实�?2. 更新相关文档内容
3. 确保示例代码可以正常运行
4. 更新�?README 的更新日�?
---

**LifeTrace 文档中心** - 让您的数字生活搜索更智能 🎉
