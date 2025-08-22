# LifeTrace Documentation Center

This folder contains all usage instructions and technical documentation for the LifeTrace system, updated according to the latest code.

## 📚 Document List

### Core Functionality Documentation

#### 1. [OCR_Optimization_Guide.md](./OCR_优化说明.md)
- **Content**: OCR performance optimization solution, migration from PaddleOCR to RapidOCR
- **Target Audience**: Developers, system administrators
- **Updated Content**: 
  - Added LifeTrace system integration methods
  - Updated vector database integration information
  - Corrected usage methods and startup commands

#### 2. [RapidOCR_Integration_Guide.md](./RapidOCR集成说明.md)
- **Content**: Detailed instructions for integrating RapidOCR engine into LifeTrace
- **Target Audience**: Developers
- **Updated Content**:
  - Added vector database integration functionality
  - Updated startup methods and programmatic usage
  - Corrected service port numbers

### Search Functionality Documentation

#### 3. [Multimodal_Search_Guide.md](./multimodal_search_guide.md)
- **Content**: Complete guide for multimodal search functionality
- **Target Audience**: Users, developers
- **Updated Content**:
  - Corrected service startup commands and port numbers
  - Updated API interface addresses
  - Maintained latest feature descriptions

#### 4. [Vector_Database_Usage_Guide.md](./vector_db_usage.md)
- **Content**: Vector database usage guide
- **Target Audience**: Developers, advanced users
- **Updated Content**:
  - Corrected port numbers for all API endpoints
  - Added multimodal search API documentation
  - Updated usage examples

#### 5. [Text_to_Image_Similarity_Usage.md](./text_to_image_similarity_usage.md)
- **Content**: Text-to-image similarity calculation program usage instructions
- **Target Audience**: Users, developers
- **Updated Content**:
  - Added Web API usage methods (recommended)
  - Updated system integration information
  - Maintained command-line usage methods

#### 6. [Image_Similarity_README.md](./README_image_similarity.md)
- **Content**: Detailed documentation for image similarity calculation program
- **Target Audience**: Developers, technical users
- **Updated Content**:
  - Added Web API usage methods
  - Updated system integration status
  - Corrected technical implementation descriptions

### Frontend Integration Documentation

#### 7. [Frontend_Integration_Guide.md](./前端集成说明.md)
- **Content**: Integration instructions for React frontend with LifeTrace backend
- **Target Audience**: Frontend developers
- **Updated Content**:
  - Corrected backend service port numbers
  - Maintained latest integration architecture descriptions
  - Updated functionality verification results

## 🚀 Quick Start

### System Startup
```bash
# Start complete LifeTrace service
python -m lifetrace_backend.server --port 8840
```

### Main Features
1. **OCR Text Recognition**: Automatically recognizes text content in screenshots
2. **Semantic Search**: Intelligent search based on text semantics
3. **Multimodal Search**: Comprehensive search combining text and images
4. **Vector Database**: Efficient semantic similarity computation
5. **Web Interface**: User-friendly interaction interface

## 📖 Usage Recommendations

### New Users
1. First read [Multimodal_Search_Guide.md](./multimodal_search_guide.md) to understand core functionality
2. Refer to [Frontend_Integration_Guide.md](./前端集成说明.md) to understand interface usage
3. Check [OCR_Optimization_Guide.md](./OCR_优化说明.md) to understand performance optimization

### Developers
1. Read [RapidOCR_Integration_Guide.md](./RapidOCR集成说明.md) to understand technical architecture
2. Refer to [Vector_Database_Usage_Guide.md](./vector_db_usage.md) to understand API usage
3. Check [Text_to_Image_Similarity_Usage.md](./text_to_image_similarity_usage.md) to understand similarity computation

### Advanced Users
1. Refer to [Image_Similarity_README.md](./README_image_similarity.md) for deep customization
2. Use command-line tools for batch processing
3. Integrate with other systems through APIs

## 🔧 Technology Stack

- **OCR Engine**: RapidOCR (replacing PaddleOCR)
- **Multimodal Model**: CLIP (OpenAI)
- **Vector Database**: ChromaDB (3 instances: text vectors, multimodal text, multimodal images)
- **Backend Framework**: FastAPI
- **Frontend Framework**: React + TypeScript
- **Database**: SQLite

### Vector Database Architecture
LifeTrace uses ChromaDB as the vector database backend, with 3 independent vector database instances deployed:

1. **Text Vector Database** (`lifetrace_ocr`)
   - Storage directory: `vector_db/`
   - Purpose: Semantic search for OCR-recognized text
   - Model: sentence-transformers

2. **Multimodal Text Vector Database** (`lifetrace_text`)
   - Storage directory: `vector_db_text/`
   - Purpose: Text embeddings for multimodal search
   - Model: CLIP text encoder

3. **Multimodal Image Vector Database** (`lifetrace_image`)
   - Storage directory: `vector_db_image/`
   - Purpose: Image embeddings for multimodal search
   - Model: CLIP image encoder

This layered architecture design ensures independence and performance optimization for different search modes.

## 📝 Update Log

### 2025-01-19
- ✅ All documents moved to `doc/` folder
- ✅ Updated all document content according to latest code
- ✅ Corrected port numbers and API addresses
- ✅ Added Web API usage methods
- ✅ Updated system integration information
- ✅ Corrected vector database technology stack description (sqlite-vec to ChromaDB)
- ✅ Added detailed vector database architecture description

## 🤝 Contributing

If you find errors in the documentation or need additions, please:
1. Check the corresponding source code to confirm the latest implementation
2. Update relevant document content
3. Ensure example code runs correctly
4. Update the changelog in this README

---

**LifeTrace Documentation Center** - Making your digital life search smarter 🎉
