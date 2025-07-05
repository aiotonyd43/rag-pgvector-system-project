from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DocumentResponse(BaseModel):
    id: str
    size: int
    created_at: datetime

class KnowledgeListResponse(BaseModel):
    documents: List[DocumentResponse]

class AuditResponse(BaseModel):
    chat_id: str
    question: str
    response: str
    retrieved_docs: List[dict]
    latency_ms: int
    timestamp: datetime
    feedback: Optional[str] = None