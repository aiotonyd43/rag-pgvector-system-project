import os

class Settings():
    # Application
    app_name: str = os.getenv("APP_NAME", "Knowledge Base System")
    app_port: int = int(os.getenv("APP_PORT", 8000))
    debug_env = os.getenv("DEBUG", "false").lower()
    debug: bool = False if debug_env == "false" else True
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Gemini Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database Configuration
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "password")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: str = os.getenv("POSTGRES_PORT", "5432")
    postgres_db: str = os.getenv("POSTGRES_DB", "knowledge_db")
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def sync_database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    # Vector Store Configuration
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
    vector_dimension: int = int(os.getenv("VECTOR_DIMENSION", 768))
    
    # Performance Settings
    max_response_latency_ms: int = int(os.getenv("MAX_RESPONSE_LATENCY_MS", 500))
    max_input_tokens: int = int(os.getenv("MAX_INPUT_TOKENS", 500))
    
    # Chunking Settings
    chunk_size: int = int(os.getenv("CHUNK_SIZE", 1000))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", 200))

settings = Settings()