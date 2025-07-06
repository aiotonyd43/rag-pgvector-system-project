import sys
import os
import http
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from apis.models.base import GenericResponseModel
from apis.models.requests import KnowledgeUpdateRequest
from apis.models.responses import KnowledgeListResponse, KnowledgeUpdateResponse, DocumentMetadata
from apis.dependencies.database import get_database
from services.knowledge_service import KnowledgeService
from utils.helper import build_api_response
from logs import logger

router = APIRouter(tags=["knowledge"])

@router.post('/knowledge/update', response_model=GenericResponseModel)
async def update_knowledge(
    request: KnowledgeUpdateRequest,
    db: AsyncSession = Depends(get_database)
):
    """Update knowledge base with new documents"""
    try:
        knowledge_service = KnowledgeService(db)
        
        # Convert request to documents format
        documents = []
        for doc_input in request.documents:
            documents.append({
                'content': doc_input.content,
                'metadata': doc_input.metadata
            })
        
        # Process documents
        result = await knowledge_service.update_knowledge(documents)
        
        # Check for errors
        if 'error' in result:
            logger.error(f"Knowledge update failed: {result['error']}")
            return build_api_response(GenericResponseModel(
                message="Failed to update knowledge base",
                data=result,
                error=True,
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR
            ))
        
        # Create response
        response_data = KnowledgeUpdateResponse(
            processed_count=result['processed_count'],
            success_count=result['success_count'],
            failed_count=result['failed_count'],
            document_ids=result['document_ids']
        )
        
        return build_api_response(GenericResponseModel(
            message=f"Successfully processed {result['success_count']} documents",
            data=response_data.dict(),
            status_code=http.HTTPStatus.OK
        ))
        
    except Exception as e:
        logger.error(f"Error in update_knowledge endpoint: {e}")
        return build_api_response(GenericResponseModel(
            message=f"Internal server error: {str(e)}",
            error=True,
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR
        ))

@router.delete('/knowledge/{document_id}', response_model=GenericResponseModel)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Delete a document from knowledge base"""
    try:
        knowledge_service = KnowledgeService(db)
        
        # Delete document
        result = await knowledge_service.delete_document(document_id)
        
        if result:
            return build_api_response(GenericResponseModel(
                message=f"Document {document_id} deleted successfully",
                data={"deleted": True, "document_id": document_id},
                status_code=http.HTTPStatus.OK
            ))
        else:
            return build_api_response(GenericResponseModel(
                message=f"Document {document_id} not found",
                error=True,
                status_code=http.HTTPStatus.NOT_FOUND
            ))
        
    except Exception as e:
        logger.error(f"Error in delete_document endpoint: {e}")
        return build_api_response(GenericResponseModel(
            message=f"Internal server error: {str(e)}",
            error=True,
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR
        ))

@router.get('/knowledge', response_model=GenericResponseModel)
async def get_knowledge(
    db: AsyncSession = Depends(get_database)
):
    """Get all documents from knowledge base"""
    try:
        knowledge_service = KnowledgeService(db)
        
        # Get all documents
        result = await knowledge_service.get_all_documents()
        
        # Convert to response format
        documents = []
        for doc in result['documents']:
            documents.append(DocumentMetadata(
                id=doc['id'],
                size=doc['size'],
                created_at=doc['created_at']
            ))
        
        response_data = KnowledgeListResponse(
            documents=documents,
            total_count=result['total_count']
        )
        
        return build_api_response(GenericResponseModel(
            message=f"Retrieved {result['total_count']} documents",
            data=response_data.model_dump(),
            status_code=http.HTTPStatus.OK
        ))
        
    except Exception as e:
        logger.error(f"Error in get_knowledge endpoint: {e}")
        return build_api_response(GenericResponseModel(
            message=f"Internal server error: {str(e)}",
            error=True,
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR
        ))

@router.get('/knowledge/search', response_model=GenericResponseModel)
async def search_knowledge(
    query: str,
    limit: int = 10,
    threshold: float = 0.7,
    db: AsyncSession = Depends(get_database)
):
    """Search documents in knowledge base"""
    try:
        knowledge_service = KnowledgeService(db)
        
        # Search documents
        results = await knowledge_service.search_documents(
            query=query,
            limit=limit,
            similarity_threshold=threshold
        )
        
        return build_api_response(GenericResponseModel(
            message=f"Found {len(results)} matching documents",
            data={
                "query": query,
                "results": results,
                "count": len(results)
            },
            status_code=http.HTTPStatus.OK
        ))
        
    except Exception as e:
        logger.error(f"Error in search_knowledge endpoint: {e}")
        return build_api_response(GenericResponseModel(
            message=f"Internal server error: {str(e)}",
            error=True,
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR
        ))
