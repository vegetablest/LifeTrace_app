# LifeTrace Vector Database Usage Guide

## Overview

LifeTrace now supports vector database functionality, enabling semantic search of OCR-recognized text content. The vector database works in parallel with the existing SQLite database without affecting original functionality.

## Features

- **Semantic Search**: Intelligent search based on text semantics rather than keyword matching
- **Auto Sync**: OCR results automatically added to vector database
- **Reranking**: Uses CrossEncoder to improve search result quality
- **Parallel Storage**: Works in parallel with SQLite database without interference
- **Configurable**: Supports multiple configuration options and model selection

## Dependency Installation

First install vector database related dependencies:

```bash
pip install -r requirements.txt
```

Main dependencies include:
- `sentence-transformers`: Text embedding models
- `chromadb`: Vector database
- `cross-encoder`: Reranking models
- `google-generativeai`: Generative AI (optional)

## Configuration

Vector database configuration is located in the `lifetrace_backend/config.py` file under the `VECTOR_DB_CONFIG` section:

```python
VECTOR_DB_CONFIG = {
    'enabled': True,  # Enable vector database
    'collection_name': 'lifetrace_ocr',  # Collection name
    'embedding_model': 'shibing624/text2vec-base-chinese',  # Embedding model
    'rerank_model': 'BAAI/bge-reranker-base',  # Reranking model
    'persist_directory': 'vector_db',  # Persistence directory
    'chunk_size': 512,  # Text chunk size
    'chunk_overlap': 50,  # Text chunk overlap
    'batch_size': 32,  # Batch processing size
    'auto_sync': True,  # Auto sync
    'sync_interval': 300  # Sync interval (seconds)
}
```

### Configuration Options

- `enabled`: Whether to enable vector database functionality
- `collection_name`: ChromaDB collection name
- `embedding_model`: Text embedding model, Chinese models recommended
- `rerank_model`: Reranking model for improving search accuracy
- `persist_directory`: Vector database persistent storage directory
- `chunk_size`: Size for long text chunking
- `chunk_overlap`: Overlapping characters between text chunks
- `batch_size`: Batch processing size, affects processing speed
- `auto_sync`: Whether to automatically add new OCR results to vector database
- `sync_interval`: Time interval for automatic synchronization

## API Usage

### 1. Semantic Search

```bash
curl -X POST "http://localhost:8840/api/semantic-search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "programming language",
       "top_k": 10,
       "use_rerank": true
     }'
```

### 2. Multimodal Search (Recommended)

```bash
curl -X POST "http://localhost:8840/api/multimodal-search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "programming language",
       "top_k": 10,
       "text_weight": 0.6,
       "image_weight": 0.4
     }'
```

### 3. Get Statistics

```bash
curl "http://localhost:8840/api/vector-stats"
```

### 4. Sync Database

```bash
curl -X POST "http://localhost:8840/api/vector-sync?limit=100"
```

### 5. Reset Vector Database

```bash
curl -X POST "http://localhost:8840/api/vector-reset"
```

## Python Code Examples

### Basic Usage

```python
from lifetrace_backend.config import config
from lifetrace_backend.components.storage import db_manager
from lifetrace_backend.components.vector_service import create_vector_service

# Initialize vector service
vector_service = create_vector_service(config, db_manager)

# Check service status
if vector_service.is_enabled():
    print("Vector database service enabled")
else:
    print("Vector database service disabled")

# Semantic search
results = vector_service.semantic_search(
    query="Python programming",
    top_k=5,
    use_rerank=True
)

for result in results:
    print(f"Similarity: {result['score']:.3f}")
    print(f"Text: {result['text'][:100]}...")
    print("---")
```

### Sync Existing Data

```python
# Sync all OCR results from SQLite database
synced_count = vector_service.sync_from_database()
print(f"Synced {synced_count} records")

# Limit sync count
synced_count = vector_service.sync_from_database(limit=1000)
print(f"Synced {synced_count} records")
```

### Get Statistics

```python
stats = vector_service.get_stats()
print(f"Vector database stats: {stats}")
```

## Testing Functionality

Run test script to verify vector database functionality:

```bash
python lifetrace_backend/components/test_vector_db.py
```

The test script verifies:
1. Vector service initialization
2. OCR results added to vector database
3. Semantic search functionality
4. Data synchronization functionality
5. Statistics information retrieval

## Performance Optimization Recommendations

### 1. Model Selection

- **Chinese scenarios**: Use `shibing624/text2vec-base-chinese`
- **English scenarios**: Use `sentence-transformers/all-MiniLM-L6-v2`
- **Multilingual scenarios**: Use `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

### 2. Hardware Configuration

- **CPU**: Multi-core CPU can improve batch processing speed
- **Memory**: Recommend at least 8GB RAM
- **Storage**: SSD can improve vector database read/write speed

### 3. Configuration Optimization

```python
VECTOR_DB_CONFIG = {
    'batch_size': 64,  # Increase batch size (if memory sufficient)
    'chunk_size': 256,  # Reduce chunk size to improve search accuracy
    'chunk_overlap': 25,  # Appropriately reduce overlap to save storage
}
```

## Troubleshooting

### 1. Dependency Issues

If encountering dependency installation issues:
```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# If encountering network issues, use domestic mirror
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 2. Model Download Issues

Models are automatically downloaded on first use. If download fails:

```python
# Manually download model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('shibing624/text2vec-base-chinese')
```

### 3. Out of Memory

If encountering out of memory issues:
1. Reduce `batch_size`
2. Use smaller models
3. Process data in batches

### 4. Inaccurate Search Results

1. Enable reranking functionality (`use_rerank: true`)
2. Adjust `retrieve_k` parameter
3. Use more suitable embedding models

## Important Notes

1. **Data Consistency**: Vector database and SQLite database store independently. Deleting data from SQLite won't automatically delete corresponding data from vector database
2. **Storage Space**: Vector database will occupy additional storage space. Regular cleanup of unnecessary data is recommended
3. **Initial Sync**: If there's a large amount of historical data, initial sync may take considerable time
4. **Model Updates**: After changing embedding models, vector database needs to be rebuilt

## Advanced Usage

### Custom Filters

```python
# Filter by application
results = vector_service.semantic_search(
    query="programming",
    filters={"application": "VSCode"}
)

# Filter by time range
results = vector_service.semantic_search(
    query="meeting",
    filters={
        "created_at": {
            "$gte": "2024-01-01T00:00:00",
            "$lt": "2024-02-01T00:00:00"
        }
    }
)
```

### Batch Operations

```python
# Batch add OCR results
with db_manager.get_session() as session:
    ocr_results = session.query(OCRResult).limit(100).all()
    
    for ocr_result in ocr_results:
        screenshot = session.query(Screenshot).filter(
            Screenshot.id == ocr_result.screenshot_id
        ).first()
        
        vector_service.add_ocr_result(ocr_result, screenshot)
```

## Current Implementation Features

### Database-Driven Architecture
- Automatic OCR data synchronization to vector database
- Real-time embedding generation and storage
- Efficient similarity search with ChromaDB

### Vector Service Integration
- Seamless integration with existing OCR pipeline
- Automatic text embedding generation
- Support for batch processing and incremental updates

### Error Handling
- Graceful fallback when vector database unavailable
- Comprehensive logging for debugging
- Robust error recovery mechanisms

### Configuration Options
- Flexible model selection for different languages
- Configurable batch sizes for performance tuning
- Optional reranking for improved search quality

## Summary

Vector database functionality provides LifeTrace with powerful semantic search capabilities, helping users more intelligently retrieve and analyze historical records. Through proper configuration and usage, it can significantly improve user experience and data utilization efficiency.
