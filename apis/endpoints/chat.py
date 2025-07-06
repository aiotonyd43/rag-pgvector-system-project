import sys
import os
import json
import http
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from apis.models.base import GenericResponseModel
from apis.models.requests import ChatRequest
from apis.models.responses import ChatResponse
from apis.dependencies.database import get_database
from services.chat_service import ChatService
from utils.helper import build_api_response
from utils.logger import logger

router = APIRouter(tags=["chat"])

@router.post('/chat', response_model=GenericResponseModel)
async def chat_non_streaming(
    request: ChatRequest,
    db: AsyncSession = Depends(get_database)
):
    """Chat endpoint with non-streaming response"""
    try:
        chat_service = ChatService(db)
        
        # Process chat query
        result = await chat_service.process_chat_query(
            query=request.query,
            chat_id=request.chat_id
        )
        
        # Create response
        response_data = ChatResponse(
            chat_id=result['chat_id'],
            response=result['response'],
            latency_ms=result['latency_ms']
        )
        
        return build_api_response(GenericResponseModel(
            message="Chat response generated successfully",
            data=response_data.model_dump(),
            status_code=http.HTTPStatus.OK
        ))
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return build_api_response(GenericResponseModel(
            message=f"Error processing chat: {str(e)}",
            error=True,
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR
        ))

async def generate_chat_stream(
    query: str,
    chat_id: str,
    chat_service: ChatService
) -> AsyncGenerator[str, None]:
    """Generate streaming chat response"""
    try:
        metadata_sent = False
        
        async for chunk, metadata in chat_service.process_streaming_chat(query, chat_id):
            if chunk:
                # Send response chunks
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            elif metadata:
                # Send metadata
                if metadata.get('status') == 'streaming' and not metadata_sent:
                    yield f"data: {json.dumps({'type': 'metadata', 'data': metadata})}\n\n"
                    metadata_sent = True
                elif metadata.get('status') in ['completed', 'error']:
                    yield f"data: {json.dumps({'type': 'metadata', 'data': metadata})}\n\n"
                    break
        
        # Send end signal
        yield f"data: {json.dumps({'type': 'end'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in chat stream: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@router.post('/chat/stream')
async def chat_streaming(
    request: ChatRequest,
    db: AsyncSession = Depends(get_database)
):
    """Chat endpoint with streaming response"""
    try:
        chat_service = ChatService(db)
        
        # Return streaming response
        return StreamingResponse(
            generate_chat_stream(request.query, request.chat_id, chat_service),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in streaming chat endpoint: {e}")
        return build_api_response(GenericResponseModel(
            message=f"Error processing streaming chat: {str(e)}",
            error=True,
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR
        ))

@router.post('/chat/{chat_id}/feedback', response_model=GenericResponseModel)
async def add_chat_feedback(
    chat_id: str,
    feedback: str,
    db: AsyncSession = Depends(get_database)
):
    """Add feedback to a chat interaction"""
    try:
        chat_service = ChatService(db)
        
        # Add feedback
        result = await chat_service.add_feedback(chat_id, feedback)
        
        if result:
            return build_api_response(GenericResponseModel(
                message="Feedback added successfully",
                data={"chat_id": chat_id, "feedback": feedback},
                status_code=http.HTTPStatus.OK
            ))
        else:
            return build_api_response(GenericResponseModel(
                message=f"Chat {chat_id} not found",
                error=True,
                status_code=http.HTTPStatus.NOT_FOUND
            ))
        
    except Exception as e:
        logger.error(f"Error in add_chat_feedback endpoint: {e}")
        return build_api_response(GenericResponseModel(
            message=f"Internal server error: {str(e)}",
            error=True,
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR
        ))