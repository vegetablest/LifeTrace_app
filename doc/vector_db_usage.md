# LifeTrace 向量数据库使用指南

## 概述

LifeTrace 现在支持向量数据库功能，可以对 OCR 识别的文本内容进行语义搜索。向量数据库与现有的 SQLite 数据库并行工作，不会影响原有功能。

## 功能特性

- **语义搜索**: 基于文本语义而非关键词匹配的智能搜索
- **自动同步**: OCR 结果自动添加到向量数据库
- **重排序**: 使用 CrossEncoder 提高搜索结果质量
- **并行存储**: 与 SQLite 数据库并行工作，互不干扰
- **可配置**: 支持多种配置选项和模型选择

## 依赖安装

首先安装向量数据库相关依赖：

```bash
pip install -r requirements_vector.txt
```

主要依赖包括：
- `sentence-transformers`: 文本嵌入模型
- `chromadb`: 向量数据库
- `cross-encoder`: 重排序模型
- `google-generativeai`: 生成式 AI（可选）

## 配置说明

向量数据库的配置位于 `config.yaml` 文件的 `vector_db` 部分：

```yaml
vector_db:
  enabled: true  # 启用向量数据库
  collection_name: 'lifetrace_ocr'  # 集合名称
  embedding_model: 'shibing624/text2vec-base-chinese'  # 嵌入模型
  rerank_model: 'BAAI/bge-reranker-base'  # 重排序模型
  persist_directory: 'vector_db'  # 持久化目录
  chunk_size: 512  # 文本块大小
  chunk_overlap: 50  # 文本块重叠
  batch_size: 32  # 批处理大小
  auto_sync: true  # 自动同步
  sync_interval: 300  # 同步间隔（秒）
```

### 配置选项说明

- `enabled`: 是否启用向量数据库功能
- `collection_name`: ChromaDB 集合名称
- `embedding_model`: 文本嵌入模型，推荐中文模型
- `rerank_model`: 重排序模型，用于提高搜索精度
- `persist_directory`: 向量数据库持久化存储目录
- `chunk_size`: 长文本分块的大小
- `chunk_overlap`: 文本块之间的重叠字符数
- `batch_size`: 批处理大小，影响处理速度
- `auto_sync`: 是否自动将新的 OCR 结果添加到向量数据库
- `sync_interval`: 自动同步的时间间隔

## API 使用

### 1. 语义搜索

```bash
curl -X POST "http://localhost:8843/api/semantic-search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "编程语言",
       "top_k": 10,
       "use_rerank": true
     }'
```

### 2. 多模态搜索（推荐）

```bash
curl -X POST "http://localhost:8843/api/multimodal-search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "编程语言",
       "top_k": 10,
       "text_weight": 0.6,
       "image_weight": 0.4
     }'
```

### 3. 获取统计信息

```bash
curl "http://localhost:8843/api/vector-stats"
```

### 4. 同步数据库

```bash
curl -X POST "http://localhost:8843/api/vector-sync?limit=100"
```

### 5. 重置向量数据库

```bash
curl -X POST "http://localhost:8843/api/vector-reset"
```

## Python 代码示例

### 基本使用

```python
from lifetrace.config import config
from lifetrace.storage import db_manager
from lifetrace.vector_service import create_vector_service

# 初始化向量服务
vector_service = create_vector_service(config, db_manager)

# 检查服务状态
if vector_service.is_enabled():
    print("向量数据库服务已启用")
else:
    print("向量数据库服务未启用")

# 语义搜索
results = vector_service.semantic_search(
    query="Python 编程",
    top_k=5,
    use_rerank=True
)

for result in results:
    print(f"相似度: {result['score']:.3f}")
    print(f"文本: {result['text'][:100]}...")
    print("---")
```

### 同步现有数据

```python
# 从 SQLite 数据库同步所有 OCR 结果
synced_count = vector_service.sync_from_database()
print(f"同步了 {synced_count} 条记录")

# 限制同步数量
synced_count = vector_service.sync_from_database(limit=1000)
print(f"同步了 {synced_count} 条记录")
```

### 获取统计信息

```python
stats = vector_service.get_stats()
print(f"向量数据库统计: {stats}")
```

## 测试功能

运行测试脚本验证向量数据库功能：

```bash
python test_vector_db.py
```

测试脚本会验证：
1. 向量服务初始化
2. OCR 结果添加到向量数据库
3. 语义搜索功能
4. 数据同步功能
5. 统计信息获取

## 性能优化建议

### 1. 模型选择

- **中文场景**: 使用 `shibing624/text2vec-base-chinese`
- **英文场景**: 使用 `sentence-transformers/all-MiniLM-L6-v2`
- **多语言场景**: 使用 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

### 2. 硬件配置

- **CPU**: 多核 CPU 可以提高批处理速度
- **内存**: 建议至少 8GB RAM
- **存储**: SSD 可以提高向量数据库读写速度

### 3. 配置优化

```yaml
vector_db:
  batch_size: 64  # 增加批处理大小（如果内存充足）
  chunk_size: 256  # 减少块大小以提高搜索精度
  chunk_overlap: 25  # 适当减少重叠以节省存储
```

## 故障排除

### 1. 依赖问题

如果遇到依赖安装问题：

```bash
# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements_vector.txt

# 如果遇到网络问题，使用国内镜像
pip install -r requirements_vector.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 2. 模型下载问题

首次使用时会自动下载模型，如果下载失败：

```python
# 手动下载模型
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('shibing624/text2vec-base-chinese')
```

### 3. 内存不足

如果遇到内存不足问题：

1. 减少 `batch_size`
2. 使用更小的模型
3. 分批处理数据

### 4. 搜索结果不准确

1. 启用重排序功能 (`use_rerank: true`)
2. 调整 `retrieve_k` 参数
3. 使用更适合的嵌入模型

## 注意事项

1. **数据一致性**: 向量数据库与 SQLite 数据库独立存储，删除 SQLite 中的数据不会自动删除向量数据库中的对应数据

2. **存储空间**: 向量数据库会占用额外的存储空间，建议定期清理不需要的数据

3. **首次同步**: 如果有大量历史数据，首次同步可能需要较长时间

4. **模型更新**: 更换嵌入模型后需要重新构建向量数据库

## 高级用法

### 自定义过滤器

```python
# 按应用程序过滤
results = vector_service.semantic_search(
    query="编程",
    filters={"application": "VSCode"}
)

# 按时间范围过滤
results = vector_service.semantic_search(
    query="会议",
    filters={
        "created_at": {
            "$gte": "2024-01-01T00:00:00",
            "$lt": "2024-02-01T00:00:00"
        }
    }
)
```

### 批量操作

```python
# 批量添加 OCR 结果
with db_manager.get_session() as session:
    ocr_results = session.query(OCRResult).limit(100).all()
    
    for ocr_result in ocr_results:
        screenshot = session.query(Screenshot).filter(
            Screenshot.id == ocr_result.screenshot_id
        ).first()
        
        vector_service.add_ocr_result(ocr_result, screenshot)
```

## 总结

向量数据库功能为 LifeTrace 提供了强大的语义搜索能力，可以帮助用户更智能地检索和分析历史记录。通过合理的配置和使用，可以显著提升用户体验和数据利用效率。