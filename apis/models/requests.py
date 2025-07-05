from pydantic import BaseModel
from typing import List, Optional

class DocumentInput(BaseModel):
    content: str
    metadata: Optional[dict] = {}

class KnowledgeUpdateRequest(BaseModel):
    documents: List[DocumentInput]

class ChatRequest(BaseModel):
    query: str
    chat_id: Optional[str] = None