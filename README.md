# LifeTrace - Intelligent Life Recording System

## Project Overview

LifeTrace is an AI-powered intelligent life recording system that helps users record and retrieve daily activities through automatic screenshot capture, OCR text recognition, and multimodal search technologies. The system supports traditional keyword search, semantic search, and multimodal search, providing powerful life trajectory tracking capabilities.

## Core Features

- **Automatic Screenshot Recording**: Timed automatic screen capture to record user activities
- **Intelligent OCR Recognition**: Uses RapidOCR to extract text content from screenshots
- **Multimodal Search**: Supports text, image, and semantic search
- **Vector Database**: Efficient vector storage and retrieval based on ChromaDB
- **Web API Service**: Provides complete RESTful API interfaces
- **Frontend Integration**: Supports integration with various frontend frameworks

## Backend Architecture

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                   LifeTrace Backend Architecture            │
├─────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│ │  Web API   │   │ Frontend UI │   │ Admin Tools │     │
│ │(FastAPI)   │   │            │   │            │     │
│ └─────────────┘   └─────────────┘   └─────────────┘     │
│        │                  │                  │          │
│        └───────────────────┼───────────────────┘          │
│                            │                              │
│ ┌─────────────────────────────────────────────────────────┐│
│ │                  Core Services                         ││
│ ├─────────────────────────────────────────────────────────┤│
│ │                                                        ││
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     ││
│ │ │Screenshot   │ │File         │ │OCR          │     ││
│ │ │Recorder     │ │Processor    │ │Service      │     ││
│ │ └─────────────┘ └─────────────┘ └─────────────┘     ││
│ │        │               │               │            ││
│ │        └────────────────┼────────────────┘            ││
│ │                         │                             ││
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     ││
│ │ │Vector       │ │Multimodal   │ │Storage      │     ││
│ │ │Service      │ │Service      │ │Manager      │     ││
│ │ └─────────────┘ └─────────────┘ └─────────────┘     ││
│ └─────────────────────────────────────────────────────────┘│
│                            │                              │
│ ┌─────────────────────────────────────────────────────────┐│
│ │                  Data Storage                          ││
│ ├─────────────────────────────────────────────────────────┤│
│ │                                                        ││
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     ││
│ │ │SQLite DB    │ │Vector DB    │ │File Storage │     ││
│ │ │Metadata     │ │ChromaDB     │ │Screenshots  │     ││
│ │ └─────────────┘ └─────────────┘ └─────────────┘     ││
│ └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Core Module Details

#### 1. Web API Service (`lifetrace_backend/server.py`)

RESTful API service built on FastAPI, providing the following main endpoints:

- **Screenshot Management**
  - `GET /api/screenshots` - Get screenshot list
  - `GET /api/screenshots/{id}` - Get single screenshot details
  - `GET /api/screenshots/{id}/image` - Get screenshot image file

- **Search Services**
  - `POST /api/search` - Traditional keyword search
  - `POST /api/semantic-search` - Semantic search
  - `POST /api/multimodal-search` - Multimodal search

- **System Management**
  - `GET /api/statistics` - Get system statistics
  - `GET /api/config` - Get system configuration
  - `GET /api/health` - Health check
  - `POST /api/cleanup` - Clean old data

- **Vector Database Management**
  - `GET /api/vector-stats` - Vector database statistics
  - `POST /api/vector-sync` - Sync vector database
  - `POST /api/vector-reset` - Reset vector database

#### 2. Data Models (`lifetrace_backend/models.py`)

Defines the core data models of the system:
- **Screenshot**: Screenshot record model
- **OCRResult**: OCR recognition result model
- **SearchIndex**: Search index model
- **ProcessingQueue**: Processing queue model

#### 3. Configuration Management (`lifetrace_backend/config.py`)

Unified configuration management system:
- Supports YAML configuration files
- Environment variable override
- Default configuration
- Configuration validation and type conversion

#### 4. Storage Management (`lifetrace_backend/storage.py`)

Database management and storage services:
- **DatabaseManager**: SQLite database management
- Transaction management support
- Automatic database migration
- Connection pool management
- Data cleanup and maintenance

#### 5. OCR Processing Module (`lifetrace_backend/simple_ocr.py`)

Image text recognition service:
- **SimpleOCRProcessor**: Text recognition based on RapidOCR
- Supports multiple image formats
- Batch processing capability
- Result caching mechanism
- Integration with vector services

#### 6. Vector Services

##### 6.1 Text Vector Service (`lifetrace_backend/vector_service.py`)

- **VectorService**: Text semantic search service
- Text embedding based on sentence-transformers
- ChromaDB vector database storage
- Supports reranking
- Automatic synchronization mechanism

##### 6.2 Multimodal Vector Service (`lifetrace_backend/multimodal_vector_service.py`)

- **MultimodalVectorService**: Image + text joint search
- Multimodal embedding based on CLIP model
- Separate text and image vector storage
- Weight fusion search algorithm
- Cross-modal semantic understanding

#### 7. File Processing Module (`lifetrace_backend/processor.py`)

File system monitoring and processing:
- **FileProcessor**: File monitoring and processing
- **ScreenshotHandler**: Screenshot file event handling
- Asynchronous processing queue
- File change monitoring
- Batch processing optimization

#### 8. Screen Recording Module (`lifetrace_backend/recorder.py`)

Automatic screenshot functionality:
- **ScreenRecorder**: Screen recording management
- Multi-screen support
- Intelligent deduplication mechanism
- Configurable screenshot interval
- Active window information acquisition

#### 9. Utility Module (`lifetrace_backend/utils.py`)

Common utility functions:
- Log configuration management
- File hash calculation
- Active window information acquisition
- Cross-platform compatibility
- File cleanup tools

### Data Flow Architecture
```
Screenshot → File Monitor → OCR Process → Vector → Storage
    ↓          ↓           ↓          ↓       ↓
Scheduled   File Events  Text Extract Embedding Database
    ↓          ↓           ↓          ↓       ↓
Multi-screen Queue Process RapidOCR   CLIP    SQLite
                                      ↓       ↓
                                   Vector DB
                                  (ChromaDB)
```

### Search Architecture

```
User Query
    ↓
┌─────────────┬─────────────┬─────────────┐
│Keyword      │ Semantic    │Multimodal   │
│Search       │ Search      │Search       │
├─────────────┼─────────────┼─────────────┤
│SQL LIKE     │Vector       │Image-Text   │
│Full-text    │Similarity   │Fusion       │
│Exact Match  │Semantic     │CLIP Model   │
│             │Understanding│Cross-modal  │
└─────────────┴─────────────┴─────────────┘
    ↓            ↓            ↓
Result Ranking → Reranking → Weight Fusion
    ↓
Unified Result Format
```

## Technology Stack

### Backend Core
- **FastAPI**: Web framework and API service
- **SQLAlchemy**: ORM and database operations
- **SQLite**: Main database
- **ChromaDB**: Vector database

### AI/ML Components
- **RapidOCR**: Text recognition engine
- **sentence-transformers**: Text embedding models
- **CLIP**: Multimodal embedding model
- **transformers**: Transformer model library

### System Tools
- **Pillow**: Image processing
- **watchdog**: File system monitoring
- **psutil**: System information acquisition
- **pydantic**: Data validation

## Deployment and Configuration

### Environment Requirements
- Python 3.8+
- Supported OS: Windows, macOS, Linux
- Optional: CUDA support (for GPU acceleration)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configuration File
Main configuration file: `config/default_config.yaml`

```yaml
server:
  host: 127.0.0.1
  port: 8840
  debug: false

vector_db:
  enabled: true
  collection_name: "lifetrace_ocr"
  embedding_model: "shibing624/text2vec-base-chinese"
  rerank_model: "BAAI/bge-reranker-base"
  persist_directory: "vector_db"

multimodal:
  enabled: true
  text_weight: 0.6
  image_weight: 0.4
```

### Starting Services

#### Start All Services
```bash
python start_all_services.py
```

#### Start Web Service Only
```bash
python -m lifetrace_backend.server --port 8840
```

#### Start Individual Services
```bash
# Start recorder
python -m lifetrace_backend.recorder

# Start processor
python -m lifetrace_backend.processor

# Start OCR service
python -m lifetrace_backend.simple_ocr
```

## API Documentation

After starting the service, access API documentation at:
- Swagger UI: http://localhost:8840/docs
- ReDoc: http://localhost:8840/redoc

## Development Guide

### Project Structure
```
LifeTrace/
├── lifetrace_backend/      # Core modules
│   ├── server.py           # Web API service
│   ├── models.py           # Data models
│   ├── config.py           # Configuration management
│   ├── storage.py          # Storage management
│   ├── simple_ocr.py       # OCR processing
│   ├── vector_service.py   # Vector service
│   ├── multimodal_*.py     # Multimodal services
│   ├── processor.py        # File processing
│   ├── recorder.py         # Screen recording
│   └── utils.py            # Utility functions
├── config/                 # Configuration files
├── doc/                    # Documentation
├── data/                   # Data directory
├── logs/                   # Log directory
└── requirements.txt        # Dependencies
```

### Extension Development
1. **Add new search algorithms**: Extend `vector_service.py`
2. **Support new OCR engines**: Modify `simple_ocr.py`
3. **Add new API endpoints**: Extend `server.py`
4. **Custom data models**: Modify `models.py`

## Performance Optimization

### Vector Database Optimization
- Regular index rebuilding
- Batch insert optimization
- Memory usage monitoring

### OCR Processing Optimization
- Image preprocessing
- Batch processing
- Result caching

### Search Performance Optimization
- Result pagination
- Query caching
- Index optimization

## Monitoring and Maintenance

### Log Management
- Log files: `logs/lifetrace_YYYYMMDD.log`
- Log levels: DEBUG, INFO, WARNING, ERROR

### Database Maintenance
- Regular cleanup of old data
- Database backup
- Index rebuilding

### System Monitoring
- Service health check: `GET /api/health`
- System statistics: `GET /api/statistics`
- Queue status: `GET /api/queue/status`

## Troubleshooting

### Common Issues

1. **Vector database initialization failure**
   - Check ChromaDB dependency installation
   - Verify data directory permissions

2. **Poor OCR recognition quality**
   - Adjust image preprocessing parameters
   - Check RapidOCR model files

3. **Multimodal search unavailable**
   - Install CLIP-related dependencies
   - Check model download status

### Debug Mode
```bash
python -m lifetrace_backend.server --debug
```

## Contributing

1. Fork the project
2. Create a feature branch
3. Commit changes
4. Create a Pull Request

## License

This project is licensed under the MIT License.

## Documentation

For detailed documentation, please refer to the `doc/` directory:
- [OCR Optimization Guide](doc/OCR_优化说明.md)
- [RapidOCR Integration Guide](doc/RapidOCR集成说明.md)
- [Multimodal Search Guide](doc/multimodal_search_guide.md)
- [Vector Database Usage Guide](doc/vector_db_usage.md)
- [Frontend Integration Guide](doc/前端集成说明.md)
- [Documentation Center](doc/README.md)
