# LifeTrace Multimodal Search Guide

## 🎯 Overview

LifeTrace multimodal search functionality considers both **text similarity** and **image similarity** to provide a more precise search experience.

### Core Technologies
- **CLIP Model**: Maps images and text to the same vector space
- **Multimodal Vector Database**: Separately stores text and image embedding vectors
- **Weight Fusion**: Configurable text/image weight combinations

## 📁 Project Structure

```
lifetrace_backend/
├── components/
│   ├── multimodal_embedding.py      # CLIP multimodal embedding generation
│   └── multimodal_vector_service.py # Multimodal vector database service
├── server.py                         # Added multimodal API endpoints
└── templates/index.html              # Frontend multimodal search interface
```

## 🔧 Technical Architecture

### 1. Embedding Generation
```
Text Content → CLIP Text Encoder → 512-dim Text Vector
Screenshot Image → CLIP Image Encoder → 512-dim Image Vector
```

### 2. Storage
```
Text Vector Database: lifetrace_text/
Image Vector Database: lifetrace_image/
```

### 3. Search Process
```
Query Text → Text Vector → Calculate similarity with stored vectors
                ↓
            Combined Score = α×Text Similarity + β×Image Similarity
```

## 🚀 Installation and Configuration

### 1. Install Dependencies
```bash
# Install multimodal dependencies
pip install -r requirements.txt
```

### 2. Configuration File
In `lifetrace_backend/config.py`:
```python
MULTIMODAL_CONFIG = {
    'enabled': True,
    'model_name': 'openai/clip-vit-base-patch32',
    'text_weight': 0.6,    # Text weight
    'image_weight': 0.4,   # Image weight
    'batch_size': 16,
    'auto_sync': True
}
```

### 3. Start Service
```bash
# Start LifeTrace service (including multimodal search)
python -m lifetrace_backend.server --port 8840

# Or use startup script
python lifetrace_backend/server.py
```

## 🎨 Frontend Interface

### Search Types
- **Traditional Search**: Based on keyword matching
- **Semantic Search**: Based on text semantic understanding
- **Multimodal Search**: Considers both text and image similarity

### Multimodal Search Options
- **Return Count**: 1-50 results
- **Text Weight**: 0.0-1.0 (default 0.6)
- **Image Weight**: 0.0-1.0 (default 0.4)

### Result Display
- **🎭 Identifier**: Multimodal search results
- **Combined Score**: Final weighted similarity
- **Detailed Scores**: Text Similarity | Image Similarity

## 📡 API Endpoints

### Multimodal Search
```http
POST /api/multimodal-search
Content-Type: application/json

{
  "query": "programming code",
  "top_k": 10,
  "text_weight": 0.6,
  "image_weight": 0.4,
  "filters": null
}
```

### Multimodal Statistics
```http
GET /api/multimodal-stats
```

### Multimodal Sync
```http
POST /api/multimodal-sync?force_reset=false
```

## 🔍 Search Strategies

### Weight Configuration Recommendations
- **Text-focused**: text_weight=0.8, image_weight=0.2
- **Balanced mode**: text_weight=0.6, image_weight=0.4
- **Image-focused**: text_weight=0.3, image_weight=0.7

### Use Cases
1. **Code Screenshots**: High text weight, recognizing code content and visual layout
2. **Interface Design**: High image weight, focusing on visual similarity
3. **Document Reading**: Balanced weight, both text content and layout matter
4. **Chart Data**: High image weight, focusing on chart shapes and structure

## 🛠️ Development and Debugging

### Test Scripts
```bash
# Test multimodal functionality
python -c "
from lifetrace_backend.components.multimodal_embedding import get_multimodal_embedding
embedding = get_multimodal_embedding()
print('Multimodal functionality available:', embedding.is_available())
"
```

### Debugging Steps
1. **Check Dependencies**: Ensure PyTorch and CLIP are installed
2. **Check Configuration**: Verify multimodal.enabled=true
3. **Check Model**: CLIP model download may take time
4. **Check Data**: Ensure screenshots and OCR data are available for search

## 📊 Performance Optimization

### Batch Processing Optimization
- Text batch encoding: 16-32 texts at once
- Image batch encoding: 8-16 images at once

### Memory Optimization
- Use CPU inference to save GPU memory
- Regularly clean vector database cache

### Search Optimization
- Pre-compute common query vectors
- Use Approximate Nearest Neighbor (ANN) algorithms

## 🔧 Troubleshooting

### Common Issues

1. **Multimodal functionality unavailable**
   ```bash
   # Check dependencies
   pip list | grep -E "(torch|transformers|clip)"
   ```

2. **Model download failure**
   ```bash
   # Set proxy or use mirror
   export HF_ENDPOINT=https://hf-mirror.com
   ```

3. **Empty search results**
   ```bash
   # Check data sync
   curl -X POST http://localhost:8840/api/multimodal-sync
   ```

4. **Out of memory**
   ```python
   # Reduce batch size in config.py
   MULTIMODAL_CONFIG = {
       'batch_size': 8
   }
   ```

### Log Analysis
```bash
# View multimodal logs
tail -f ~/.lifetrace/logs/*.log | grep -i multimodal
```

## 🚀 Future Extensions

### Model Upgrades
- Support multilingual CLIP models
- Integrate Chinese-CLIP
- Support larger CLIP models (ViT-L/14)

### Feature Enhancements
- Image-to-image search
- Cross-modal search (search text with images)
- Time series similarity

### Performance Optimization
- GPU-accelerated inference
- Vector quantization compression
- Distributed vector database

## 📈 Effectiveness Evaluation

### Search Quality Metrics
- **Precision**: Proportion of relevant results
- **Recall**: Proportion of relevant results found
- **Diversity**: Diversity level of results

### Performance Metrics
- **Search Latency**: <2 second response time
- **Sync Speed**: >100 records per minute
- **Memory Usage**: <2GB peak memory

## 🎯 Current Implementation Features

### Database-Driven Architecture
- Automatic OCR data synchronization to vector database
- Real-time embedding generation and storage
- Efficient similarity search with ChromaDB

### Vector Service Integration
- Seamless integration with existing OCR pipeline
- Automatic text and image embedding generation
- Support for batch processing and incremental updates

### Error Handling
- Graceful fallback when CLIP model unavailable
- Comprehensive logging for debugging
- Robust error recovery mechanisms

### Configuration Options
- Flexible weight adjustment for different use cases
- Configurable batch sizes for performance tuning
- Optional GPU acceleration support

Through multimodal search, LifeTrace provides a more intelligent and precise personal digital life search experience! 🎉
