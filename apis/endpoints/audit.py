import sys
import os
import http
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from apis.models.base import GenericResponseModel
from apis.models.responses import AuditResponse
from apis.dependencies.database import get_database
from services.audit_service import AuditService
from utils.helper import build_api_response
from utils.logger import logger

router = APIRouter(tags=["audit"])

@router.get('/audit/{chat_id}', response_model=GenericResponseModel)
async def get_audit(
    chat_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get audit information for a specific chat"""
    try:
        audit_service = AuditService(db)
        
        # Get audit data
        audit_data = await audit_service.get_chat_audit(chat_id)
        if audit_data:
            # Create response
            response_data = AuditResponse(
                chat_id=str(audit_data['chat_id']),
                question=audit_data['question'],
                response=audit_data['response'],
                retrieved_docs=audit_data['retrieved_docs'],
                latency_ms=audit_data['latency_ms'],
                timestamp=audit_data['timestamp'],
                feedback=audit_data['feedback']
            )
            
            return build_api_response(GenericResponseModel(
                message="Audit data retrieved successfully",
                data=response_data.dict(),
                status_code=http.HTTPStatus.OK
            ))
        else:
            return build_api_response(GenericResponseModel(
                message=f"No audit data found for chat {chat_id}",
                error=True,
                status_code=http.HTTPStatus.NOT_FOUND
            ))
        
    except Exception as e:
        logger.error(f"Error in get_audit endpoint: {e}")
        return build_api_response(GenericResponseModel(
            message="Internal server error",
            error=True,
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR
        ))
