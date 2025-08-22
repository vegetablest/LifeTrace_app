# LifeTrace - 智能生活记录系统

## 项目概述

LifeTrace 是一个基�?AI 的智能生活记录系统，通过自动截图、OCR 文本识别和多模态搜索技术，帮助用户记录和检索日常活动。系统支持传统关键词搜索、语义搜索和多模态搜索，提供强大的生活轨迹追踪能力�?
## 核心功能

- **自动截图记录**：定时自动截取屏幕内容，记录用户活动
- **智能 OCR 识别**：使�?RapidOCR 提取截图中的文本内容
- **多模态搜�?*：支持文本、图像和语义搜索
- **向量数据�?*：基�?ChromaDB 的高效向量存储和检�?- **Web API 服务**：提供完整的 RESTful API 接口
- **前端集成**：支持多种前端框架集�?
## 后端架构

### 系统架构�?
```
┌─────────────────────────────────────────────────────────────�?�?                   LifeTrace 后端架构                        �?├─────────────────────────────────────────────────────────────�?�?                                                            �?�? ┌─────────────�?   ┌─────────────�?   ┌─────────────�?     �?�? �?  Web API   �?   �? 前端界面    �?   �? 管理工具    �?     �?�? �?(FastAPI)   �?   �?            �?   �?            �?     �?�? └─────────────�?   └─────────────�?   └─────────────�?     �?�?        �?                  �?                  �?          �?�?        └───────────────────┼───────────────────�?          �?�?                            �?                              �?�? ┌─────────────────────────────────────────────────────────�?�?�? �?                  核心服务�?                            �?�?�? ├─────────────────────────────────────────────────────────�?�?�? �?                                                        �?�?�? �? ┌─────────────�? ┌─────────────�? ┌─────────────�?     �?�?�? �? �?截图记录�?  �? �?文件处理�?  �? �?OCR 处理�?  �?     �?�?�? �? �?Recorder    �? �?Processor   �? �?OCR         �?     �?�?�? �? └─────────────�? └─────────────�? └─────────────�?     �?�?�? �?        �?               �?               �?            �?�?�? �?        └────────────────┼────────────────�?            �?�?�? �?                         �?                             �?�?�? �? ┌─────────────�? ┌─────────────�? ┌─────────────�?     �?�?�? �? �?向量服务     �? �?多模态服�?  �? �?存储管理�?  �?     �?�?�? �? �?Vector      �? �?Multimodal  �? �?Storage     �?     �?�?�? �? └─────────────�? └─────────────�? └─────────────�?     �?�?�? └─────────────────────────────────────────────────────────�?�?�?                            �?                              �?�? ┌─────────────────────────────────────────────────────────�?�?�? �?                  数据存储�?                            �?�?�? ├─────────────────────────────────────────────────────────�?�?�? �?                                                        �?�?�? �? ┌─────────────�? ┌─────────────�? ┌─────────────�?     �?�?�? �? �?SQLite 数据库│  �?向量数据�?  �? �?文件存储     �?     �?�?�? �? �?元数据存�?  �? �?ChromaDB    �? �?截图文件     �?     �?�?�? �? └─────────────�? └─────────────�? └─────────────�?     �?�?�? └─────────────────────────────────────────────────────────�?�?└─────────────────────────────────────────────────────────────�?```

### 核心模块详解

#### 1. Web API �?(`lifetrace/server.py`)

基于 FastAPI 构建�?RESTful API 服务，提供以下主要端点：

- **截图管理**
  - `GET /api/screenshots` - 获取截图列表
  - `GET /api/screenshots/{id}` - 获取单个截图详情
  - `GET /api/screenshots/{id}/image` - 获取截图图片文件

- **搜索服务**
  - `POST /api/search` - 传统关键词搜�?  - `POST /api/semantic-search` - 语义搜索
  - `POST /api/multimodal-search` - 多模态搜�?
- **系统管理**
  - `GET /api/statistics` - 获取系统统计信息
  - `GET /api/config` - 获取系统配置
  - `GET /api/health` - 健康检�?  - `POST /api/cleanup` - 清理旧数�?
- **向量数据库管�?*
  - `GET /api/vector-stats` - 向量数据库统�?  - `POST /api/vector-sync` - 同步向量数据�?  - `POST /api/vector-reset` - 重置向量数据�?
#### 2. 数据模型�?(`lifetrace/models.py`)

定义了系统的核心数据模型�?
- **Screenshot**: 截图记录模型
- **OCRResult**: OCR 识别结果模型
- **SearchIndex**: 搜索索引模型
- **ProcessingQueue**: 处理队列模型

#### 3. 配置管理 (`lifetrace/config.py`)

统一的配置管理系统：

- 支持 YAML 配置文件
- 环境变量覆盖
- 默认配置�?- 配置验证和类型转�?
#### 4. 存储管理�?(`lifetrace/storage.py`)

数据库管理和存储服务�?
- **DatabaseManager**: SQLite 数据库管�?- 支持事务管理
- 自动数据库迁�?- 连接池管�?- 数据清理和维�?
#### 5. OCR 处理模块 (`lifetrace/ocr.py`)

图像文本识别服务�?
- **OCRProcessor**: 基于 RapidOCR 的文本识�?- 支持多种图像格式
- 批量处理能力
- 结果缓存机制
- 与向量服务集�?
#### 6. 向量服务�?
##### 6.1 文本向量服务 (`lifetrace/vector_service.py`)

- **VectorService**: 文本语义搜索服务
- 基于 sentence-transformers 的文本嵌�?- ChromaDB 向量数据库存�?- 支持重排序（rerank�?- 自动同步机制

##### 6.2 多模态向量服�?(`lifetrace/multimodal_vector_service.py`)

- **MultimodalVectorService**: 图像+文本联合搜索
- 基于 CLIP 模型的多模态嵌�?- 分离的文本和图像向量存储
- 权重融合搜索算法
- 跨模态语义理�?
#### 7. 文件处理模块 (`lifetrace/processor.py`)

文件系统监控和处理：

- **FileProcessor**: 文件监控和处�?- **ScreenshotHandler**: 截图文件事件处理
- 异步处理队列
- 文件变更监听
- 批量处理优化

#### 8. 屏幕录制模块 (`lifetrace/recorder.py`)

自动截图功能�?
- **ScreenRecorder**: 屏幕录制管理
- 多屏幕支�?- 智能去重机制
- 可配置截图间�?- 活跃窗口信息获取

#### 9. 工具模块 (`lifetrace/utils.py`)

通用工具函数�?
- 日志配置管理
- 文件哈希计算
- 活跃窗口信息获取
- 跨平台兼容�?- 文件清理工具

### 数据流架�?
```
截图生成 �?文件监控 �?OCR处理 �?向量�?�?存储
    �?          �?        �?       �?      �?定时任务    文件事件   文本提取  嵌入生成  数据�?    �?          �?        �?       �?      �?多屏支持    队列处理   RapidOCR  CLIP模型 SQLite
                                          �?                                    向量数据�?                                   (ChromaDB)
```

### 搜索架构

```
用户查询
    �?┌─────────────┬─────────────┬─────────────�?�?关键词搜�?  �? 语义搜索    �?多模态搜�?  �?├─────────────┼─────────────┼─────────────�?�?SQL LIKE    �?向量相似�?  �?图文融合     �?�?全文索引     �?语义理解     �?CLIP模型     �?�?精确匹配     �?模糊匹配     �?跨模态理�?  �?└─────────────┴─────────────┴─────────────�?    �?            �?            �?结果排序 �?重排序算�?�?权重融合
    �?统一结果格式
```

## 技术栈

### 后端核心
- **FastAPI**: Web 框架�?API 服务
- **SQLAlchemy**: ORM 和数据库操作
- **SQLite**: 主数据库
- **ChromaDB**: 向量数据�?
### AI/ML 组件
- **RapidOCR**: 文本识别引擎
- **sentence-transformers**: 文本嵌入模型
- **CLIP**: 多模态嵌入模�?- **transformers**: Transformer 模型�?
### 系统工具
- **Pillow**: 图像处理
- **watchdog**: 文件系统监控
- **psutil**: 系统信息获取
- **pydantic**: 数据验证

## 部署和配�?
### 环境要求
- Python 3.8+
- 支持的操作系统：Windows、macOS、Linux
- 可选：CUDA 支持（用�?GPU 加速）

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置文件
主配置文件：`config/default_config.yaml`

```yaml
server:
  host: 127.0.0.1
  port: 8840
  debug: false

vector_db:
  enabled: true
  collection_name: "lifetrace_ocr"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  rerank_model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
  persist_directory: "data/vector_db"

multimodal:
  enabled: true
  text_weight: 0.6
  image_weight: 0.4
```

### 启动服务

#### 启动所有服�?```bash
python start_all_services.py
```

#### 单独启动 Web 服务
```bash
python -m lifetrace_backend.server --port 8840
```

#### 启动前端演示
```bash
python start_frontend_demo.py
```

## API 文档

启动服务后，访问 API 文档�?- Swagger UI: http://localhost:8840/docs
- ReDoc: http://localhost:8840/redoc

## 开发指�?
### 项目结构
```
LifeTrace/
├── lifetrace/              # 核心模块
�?  ├── server.py           # Web API 服务
�?  ├── models.py           # 数据模型
�?  ├── config.py           # 配置管理
�?  ├── storage.py          # 存储管理
�?  ├── ocr.py              # OCR 处理
�?  ├── vector_service.py   # 向量服务
�?  ├── multimodal_*.py     # 多模态服�?�?  ├── processor.py        # 文件处理
�?  ├── recorder.py         # 屏幕录制
�?  └── utils.py            # 工具函数
├── config/                 # 配置文件
├── doc/                    # 文档目录
├── data/                   # 数据目录
├── logs/                   # 日志目录
└── requirements.txt        # 依赖列表
```

### 扩展开�?
1. **添加新的搜索算法**：扩�?`vector_service.py`
2. **支持新的 OCR 引擎**：修�?`ocr.py`
3. **添加新的 API 端点**：扩�?`server.py`
4. **自定义数据模�?*：修�?`models.py`

## 性能优化

### 向量数据库优�?- 定期重建索引
- 批量插入优化
- 内存使用监控

### OCR 处理优化
- 图像预处�?- 批量处理
- 结果缓存

### 搜索性能优化
- 结果分页
- 查询缓存
- 索引优化

## 监控和维�?
### 日志管理
- 日志文件：`logs/lifetrace_YYYYMMDD.log`
- 日志级别：DEBUG、INFO、WARNING、ERROR

### 数据库维�?- 定期清理旧数�?- 数据库备�?- 索引重建

### 系统监控
- 服务健康检查：`GET /api/health`
- 系统统计：`GET /api/statistics`
- 队列状态：`GET /api/queue/status`

## 故障排除

### 常见问题

1. **向量数据库初始化失败**
   - 检�?ChromaDB 依赖安装
   - 确认数据目录权限

2. **OCR 识别效果�?*
   - 调整图像预处理参�?   - 检�?RapidOCR 模型文件

3. **多模态搜索不可用**
   - 安装 CLIP 相关依赖
   - 检查模型下载状�?
### 调试模式
```bash
python -m lifetrace_backend.server --debug
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可�?
本项目采�?MIT 许可证�?
## 更多文档

详细文档请参�?`doc/` 目录�?- [OCR 优化说明](doc/OCR_优化说明.md)
- [RapidOCR 集成说明](doc/RapidOCR集成说明.md)
- [多模态搜索指南](doc/multimodal_search_guide.md)
- [向量数据库使用指南](doc/vector_db_usage.md)
- [前端集成说明](doc/前端集成说明.md)
- [文档中心](doc/README.md)
