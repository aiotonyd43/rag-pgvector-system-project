from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DocumentInput(BaseModel):
    """Single document input model"""
    content: str = Field(..., description="Document content", min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Document metadata")

class KnowledgeUpdateRequest(BaseModel):
    """Request model for updating knowledge base"""
    documents: List[DocumentInput] = Field(..., description="List of documents to add/update")

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    query: str = Field(..., description="User query", min_length=1, max_length=2000)
    chat_id: Optional[str] = Field(None, description="Optional chat ID for conversation tracking")