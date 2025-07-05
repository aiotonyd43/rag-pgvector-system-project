import os

class Settings():
    # Application
    app_name: str = os.getenv("APP_NAME", "Knowledge Base System")
    app_port: int = int(os.getenv("APP_PORT", 8000))
    debug_env = os.getenv("DEBUG", "false").lower()
    debug: bool = False if debug_env == "false" else True
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Gemini Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/knowledge_db")
    
    # Vector Store Configuration
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
    vector_dimension: int = int(os.getenv("VECTOR_DIMENSION", 768))
    
    # Performance Settings
    max_response_latency_ms: int = int(os.getenv("MAX_RESPONSE_LATENCY_MS", 500))
    max_input_tokens: int = int(os.getenv("MAX_INPUT_TOKENS", 500))

settings = Settings()