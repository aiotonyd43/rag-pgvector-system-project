# RAG Interview Project

A production-ready Retrieval-Augmented Generation (RAG) system built with FastAPI, PostgreSQL + pgvector, and Google Gemini AI. This system enables intelligent document search and AI-powered chat interactions with comprehensive audit logging.

## 🏗️ Architecture Overview

### Core Components

- **FastAPI Application**: High-performance async web framework with automatic API documentation
- **PostgreSQL + pgvector**: Vector database for efficient similarity search and document storage
- **Google Gemini AI**: Embedding generation and chat response generation
- **Docker Compose**: Multi-container deployment with service orchestration

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │    │   FastAPI API   │    │   PostgreSQL    │
│                 │◄──►│                 │◄──►│   + pgvector    │
│   (Frontend)    │    │   (Backend)     │    │   (Vector DB)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Gemini AI     │
                       │   (Embeddings   │
                       │   + Chat LLM)   │
                       └─────────────────┘
```

## 🚀 Features

### Document Management
- **Document Upload & Processing**: Automatic text chunking and embedding generation
- **Vector Storage**: Efficient storage using PostgreSQL + pgvector extension
- **Semantic Search**: Cosine similarity-based document retrieval
- **Metadata Management**: Flexible JSONB-based document metadata

### RAG Chat System
- **Context-Aware Responses**: AI responses powered by relevant document context
- **Real-time Streaming**: Server-sent events for live response streaming
- **Chat History**: Persistent chat sessions with unique identifiers
- **Feedback Collection**: User feedback integration for continuous improvement

### Monitoring & Audit
- **Comprehensive Logging**: Detailed audit trails for all interactions
- **Performance Metrics**: Response latency tracking and optimization
- **Health Monitoring**: Built-in health check endpoints
- **Error Tracking**: Structured error handling and logging

## 📋 Prerequisites

- **Python 3.13+**
- **Docker & Docker Compose**
- **Google Gemini API Key**
- **PostgreSQL** (if running locally)

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag-interview
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
# Application Settings
APP_NAME=RAG pgvector System
APP_PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=knowledge_db

# AI/ML Configuration
GEMINI_API_KEY=your_gemini_api_key_here
EMBEDDING_MODEL=text-embedding-004
VECTOR_DIMENSION=768

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 3. Docker Deployment

```bash
# Start the complete system
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### 4. Local Development Setup

```bash
# Install dependencies
pip install poetry
poetry install

# Run database migrations
# (Database schema is automatically created via init.sql)

# Start the application
poetry run python -m uvicorn apis.main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Database Schema

### Documents Table
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(768),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vector similarity index
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL,
    question TEXT NOT NULL,
    response TEXT NOT NULL,
    retrieved_docs JSONB,
    latency_ms INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    feedback TEXT
);
```

## 🔌 API Endpoints

### Knowledge Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/knowledge/update` | Upload and process documents |
| `GET` | `/api/knowledge` | List all documents |
| `DELETE` | `/api/knowledge/{document_id}` | Delete document |
| `GET` | `/api/knowledge/search` | Semantic search |

### Chat Interface

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Generate AI response |
| `POST` | `/api/chat/stream` | Streaming AI response |
| `POST` | `/api/chat/{chat_id}/feedback` | Submit feedback |

### Audit & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/audit/{chat_id}` | Get audit information |
| `GET` | `/health` | Health check |

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | `RAG pgvector System` |
| `APP_PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `POSTGRES_*` | Database connection | See .env example |
| `GEMINI_API_KEY` | Google Gemini API key | **Required** |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-004` |
| `VECTOR_DIMENSION` | Vector dimensions | `768` |
| `CHUNK_SIZE` | Document chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |

### Document Processing

- **Chunking Strategy**: Recursive character text splitter
- **Embedding Model**: Google Gemini text-embedding-004
- **Vector Dimensions**: 768
- **Similarity Metric**: Cosine distance

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Document Upload
```bash
curl -X POST "http://localhost:8000/api/knowledge/update" \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"content": "Your document content here"}]}'
```

### Chat Query
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the documents?"}'
```

## 🔍 Monitoring & Logging

### Application Logs
```bash
# View application logs
docker-compose logs -f app

# View database logs
docker-compose logs -f postgres
```

### Performance Metrics
- Response latency tracking
- Document retrieval performance
- Embedding generation time
- Database query optimization

### Health Monitoring
```bash
# Check service health
curl http://localhost:8000/health

# Check database connection
docker-compose exec postgres pg_isready -U postgres
```

## 🛡️ Security

- **Non-root Container**: Docker containers run as non-root user
- **Environment Variables**: Sensitive data managed through environment variables
- **Input Validation**: Pydantic models for request/response validation
- **Error Handling**: Comprehensive error handling without information leakage

## 📈 Performance Optimization

### Database Optimizations
- **Connection Pooling**: Async SQLAlchemy connection pooling
- **Vector Indexes**: IVFFlat indexes for efficient similarity search
- **Query Optimization**: Optimized queries with proper indexing

### Application Optimizations
- **Async Operations**: Full async/await implementation
- **Streaming Responses**: Real-time response streaming
- **Connection Reuse**: Efficient HTTP client management
- **Caching**: Strategic caching for frequently accessed data

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   docker-compose ps postgres
   
   # Verify database connectivity
   docker-compose exec postgres psql -U postgres -d knowledge_db -c "SELECT 1;"
   ```

2. **Embedding Generation Errors**
   - Verify `GEMINI_API_KEY` is set correctly
   - Check API rate limits
   - Validate document content size

3. **Vector Search Performance**
   - Ensure pgvector extension is installed
   - Check vector index creation
   - Optimize similarity threshold

### Development Tips

```bash
# Reset database
docker-compose down -v
docker-compose up -d

# View API documentation
open http://localhost:8000/docs

# Monitor application logs
docker-compose logs -f app | grep ERROR
```

## 📄 License

This project is licensed under the MIT License.
