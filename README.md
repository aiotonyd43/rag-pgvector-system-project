# RAG pgvector System Project

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
cd rag-pgvector-system-project
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

## 🤖 Agent System

The RAG system includes a powerful agent-based architecture built with LangGraph for sophisticated query processing and response generation.

### Agent Architecture

The agent system consists of:

- **Primary Answer Query Agent**: Main RAG agent that processes user queries and generates contextual responses
- **State Management**: Maintains conversation context and metadata throughout the interaction
- **Document Retrieval**: Intelligent document retrieval using pgvector similarity search
- **LLM Synthesis**: Context-aware response generation using Google Gemini

### Agent Workflow

The agent follows this 3-node processing workflow with conditional routing:

1. **Sensitive Check**: Uses LLM to analyze if query contains political or sexual content
2. **Primary Answer Query**: RAG pipeline that retrieves and synthesizes information (only if content is safe)
3. **Postprocess**: Formats final response with metadata and source information

### Agent Nodes

The LangGraph agent contains three main nodes:

#### 1. **sensitive_check**
- Analyzes incoming queries for sensitive content (politics, sexual topics)
- Uses Gemini LLM to classify content as "SENSITIVE" or "SAFE"
- If sensitive: Returns rejection message and sets `is_sensitive=True`
- If safe: Passes query to next node with `is_sensitive=False`

#### 2. **primary_answer_query**
- Main RAG processing node (only executed for safe content)
- Extracts user query from conversation messages
- Retrieves relevant documents from pgvector database using similarity search
- Synthesizes contextual response using retrieved documents and Gemini LLM
- Returns updated state with AI response and retrieved documents

#### 3. **postprocess**
- Final formatting and response preparation node
- Formats responses with proper structure and metadata
- Adds source information from retrieved documents
- Handles both sensitive content rejections and successful RAG responses
- Provides final polished output to user

### Agent State

The agent maintains state through the following structure:

```python
class State(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    remaining_steps: int
    query: str
    is_sensitive: bool
    retrieved_docs: list
```

#### State Fields

- **messages**: Conversation history using LangChain message format
- **remaining_steps**: Number of processing steps remaining
- **query**: Current user query being processed
- **is_sensitive**: Flag indicating if content contains sensitive topics
- **retrieved_docs**: Documents retrieved from vector database (for non-sensitive queries)

### Agent Flow

```
START → sensitive_check → [routing] → primary_answer_query → postprocess → END
                             ↓
                        postprocess → END
```

The agent uses conditional routing based on content sensitivity:

**Path 1 (Safe Content):**
1. `START` → `sensitive_check` (determines content is safe)
2. `sensitive_check` → `primary_answer_query` (performs RAG)
3. `primary_answer_query` → `postprocess` (formats response)
4. `postprocess` → `END`

**Path 2 (Sensitive Content):**
1. `START` → `sensitive_check` (determines content is sensitive)
2. `sensitive_check` → `postprocess` (formats rejection message)
3. `postprocess` → `END`

### Using the Agent

To interact with the agent system, run the test workflow file:

```bash
# Navigate to the project directory
cd rag-pgvector-system-project

# Run the agent test workflow
python tests/test_workflow.py
```

This will start an interactive chat session where you can test the agent's capabilities. The agent will process your queries, retrieve relevant documents from the vector database, and provide contextual responses.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | `RAG pgvector System` | No |
| `APP_PORT` | Server port | `8000` | No |
| `DEBUG` | Debug mode (true/false) | `false` | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` | No |
| `GEMINI_API_KEY` | Google Gemini API key | - | **Yes** |
| `POSTGRES_USER` | PostgreSQL username | `postgres` | No |
| `POSTGRES_PASSWORD` | PostgreSQL password | `password` | No |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` | No |
| `POSTGRES_PORT` | PostgreSQL port | `5432` | No |
| `POSTGRES_DB` | PostgreSQL database name | `knowledge_db` | No |
| `EMBEDDING_MODEL` | Gemini embedding model | `text-embedding-004` | No |
| `VECTOR_DIMENSION` | Vector dimensions | `768` | No |
| `CHUNK_SIZE` | Document chunk size | `1000` | No |
| `CHUNK_OVERLAP` | Document chunk overlap | `200` | No |

### Document Processing

- **Chunking Strategy**: Recursive character text splitter
- **Embedding Model**: Google Gemini text-embedding-004
- **Vector Dimensions**: 768
- **Similarity Metric**: Cosine distance

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

## 📄 License

This project is licensed under the MIT License.
