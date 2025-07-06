from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentMetadata(BaseModel):
    """Document metadata response model"""
    id: str = Field(..., description="Document ID")
    size: int = Field(..., description="Document size in characters")
    created_at: datetime = Field(..., description="Creation timestamp")

class KnowledgeListResponse(BaseModel):
    """Response model for knowledge list endpoint"""
    documents: List[DocumentMetadata] = Field(..., description="List of documents")
    total_count: int = Field(..., description="Total number of documents")

class KnowledgeUpdateResponse(BaseModel):
    """Response model for knowledge update endpoint"""
    processed_count: int = Field(..., description="Number of documents processed")
    success_count: int = Field(..., description="Number of successfully added documents")
    failed_count: int = Field(..., description="Number of failed documents")
    document_ids: List[str] = Field(..., description="List of created document IDs")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    chat_id: str = Field(..., description="Chat ID")
    response: str = Field(..., description="AI response")
    latency_ms: int = Field(..., description="Response latency in milliseconds")

class AuditResponse(BaseModel):
    """Response model for audit endpoint"""
    chat_id: str = Field(..., description="Chat ID")
    question: str = Field(..., description="User question")
    response: str = Field(..., description="AI response")
    retrieved_docs: List[str] = Field(..., description="Retrieved documents for context")
    latency_ms: int = Field(..., description="Response latency in milliseconds")
    timestamp: datetime = Field(..., description="Interaction timestamp")
    feedback: Optional[str] = Field(None, description="User feedback")