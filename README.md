# RAG Knowledge Base System

A containerized knowledge base system with full CRUD operations on vector data, AI chat with streaming responses, and comprehensive audit logging.

## Features

- **Vector Store Management**: Full CRUD operations on document embeddings using PostgreSQL + pgvector
- **AI Chat Interface**: RAG-powered chat with Gemini AI and streaming responses
- **Audit Logging**: Complete interaction tracking with performance metrics
- **Async Architecture**: High-performance async I/O throughout
- **Docker Support**: Fully containerized with docker-compose

## Tech Stack

- **Backend**: FastAPI with async/await
- **Database**: PostgreSQL with pgvector extension
- **AI/ML**: Google Gemini API, LangChain
- **Containerization**: Docker, docker-compose
- **Language**: Python 3.12+

## API Endpoints

### Knowledge Management
- `POST /api/knowledge/update` - Update knowledge base with documents
- `GET /api/knowledge` - List all documents with metadata
- `GET /api/knowledge/{id}` - Get specific document
- `PUT /api/knowledge/{id}` - Update document
- `DELETE /api/knowledge/{id}` - Delete document
- `GET /api/knowledge/stats/summary` - Knowledge base statistics

### Chat Interface
- `POST /api/chat` - Generate chat response
- `POST /api/chat/stream` - Generate streaming chat response
- `GET /api/chat/health` - Chat service health check

### Audit & Monitoring
- `GET /api/audit/{chat_id}` - Get audit log for chat session
- `GET /api/audit` - List audit logs with pagination
- `POST /api/audit/{chat_id}/feedback` - Add feedback to chat session
- `GET /api/audit/stats/summary` - Audit statistics
- `GET /api/audit/stats/performance` - Performance metrics

### System
- `GET /health` - System health check
- `GET /info` - Application information
- `GET /` - Root endpoint

## Quick Start

### Prerequisites
- Docker and docker-compose
- Gemini API key

### Setup

1. **Clone and setup environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

2. **Quick start with script**:
   ```bash
   ./start.sh
   ```

   Or manually:
   ```bash
   docker-compose up -d
   ```

3. **Check health**:
   ```bash
   curl http://localhost:8000/health
   ```

4. **Run tests**:
   ```bash
   python test_api.py
   ```

5. **Access API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Example Usage

1. **Add documents to knowledge base**:
   ```bash
   curl -X POST "http://localhost:8000/api/knowledge/update" \
   -H "Content-Type: application/json" \
   -d '{
     "documents": [
       {
         "content": "Python is a programming language known for its simplicity.",
         "metadata": {"source": "tutorial", "topic": "programming"}
       }
     ]
   }'
   ```

2. **Chat with the knowledge base**:
   ```bash
   curl -X POST "http://localhost:8000/api/chat" \
   -H "Content-Type: application/json" \
   -d '{
     "query": "What is Python?"
   }'
   ```

3. **Stream chat response**:
   ```bash
   curl -X POST "http://localhost:8000/api/chat/stream" \
   -H "Content-Type: application/json" \
   -d '{
     "query": "Explain machine learning"
   }'
   ```

## Configuration

Key environment variables:

```bash
# Application
APP_NAME=Knowledge Base System
APP_PORT=8000
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/knowledge_db

# AI/ML
GEMINI_API_KEY=your_gemini_api_key_here
EMBEDDING_MODEL=text-embedding-004
VECTOR_DIMENSION=768

# Performance
MAX_RESPONSE_LATENCY_MS=500
MAX_INPUT_TOKENS=500
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │────│  Vector Store   │────│   PostgreSQL    │
│   (Async I/O)   │    │   (pgvector)    │    │   + pgvector    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ├── LangChain ──────── Gemini API
         │
         └── Audit Logger ───── Performance Metrics
```

## Development

### Local Development
```bash
# Install dependencies
poetry install

# Run locally
poetry run python apis/main.py
```

### Database Schema
The system uses two main tables:
- `documents`: Stores content, embeddings, and metadata
- `audit_logs`: Tracks all interactions with performance metrics

## Performance Requirements

- **Latency**: < 500ms for inputs < 500 tokens
- **Async I/O**: All database and API operations are async
- **Vector Operations**: Full CRUD support with similarity search
- **Streaming**: Real-time response streaming for chat

## Monitoring

- Health checks for all services
- Performance metrics tracking
- Comprehensive audit logging
- Error handling and logging

## Troubleshooting

### Common Issues

1. **Import Error with 'metadata' field**:
   - SQLAlchemy reserves the `metadata` attribute
   - Solution: Use `document_metadata` in database model

2. **Gemini API Key not configured**:
   ```bash
   # Set in .env file
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Database connection issues**:
   ```bash
   # Restart database service
   docker-compose down
   docker-compose up db -d
   ```

4. **Services not starting**:
   ```bash
   # Check logs
   docker-compose logs
   
   # Rebuild containers
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Performance Tuning

- Adjust `MAX_RESPONSE_LATENCY_MS` for your needs
- Increase database connection pool size for high load
- Monitor with `/api/audit/stats/performance`

## License

This project is for interview/demonstration purposes.