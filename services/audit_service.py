import json
import sys
import os
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from logs import logger
from utils.helper import get_current_vietnam_datetime

class AuditService:
    """Service for managing audit logs"""
    
    def __init__(self, session: AsyncSession):
        """Initialize audit service with database session"""
        self.session = session
    
    async def log_chat_interaction(
        self,
        chat_id: str,
        question: str,
        response: str,
        retrieved_docs: List[Dict[str, Any]],
        latency_ms: int,
        feedback: Optional[str] = None
    ) -> str:
        """
        Log a chat interaction to audit table
        
        Args:
            chat_id: Chat session ID
            question: User question
            response: AI response
            retrieved_docs: Documents used for context
            latency_ms: Response latency in milliseconds
            feedback: Optional user feedback
            
        Returns:
            Audit log ID
        """
        try:
            # Prepare audit log entry
            audit_id = str(uuid.uuid4())
            id_retrieved_docs = [
                doc.get('id', str(uuid.uuid4())) for doc in retrieved_docs
            ]
            # convert to json string for storage
            json_id_retrieved_docs = json.dumps(id_retrieved_docs)
            
            query = text("""
                INSERT INTO audit_logs (
                    id, chat_id, question, response, retrieved_docs, 
                    latency_ms, timestamp, feedback
                )
                VALUES (
                    :id, :chat_id, :question, :response, :retrieved_docs,
                    :latency_ms, :timestamp, :feedback
                )
            """)

            insert_data = {
                'id': audit_id,
                'chat_id': chat_id,
                'question': question,
                'response': response,
                'retrieved_docs': json_id_retrieved_docs,
                'latency_ms': latency_ms,
                'timestamp': get_current_vietnam_datetime(),
                'feedback': feedback
            }

            await self.session.execute(query, insert_data)

            await self.session.commit()
            logger.info(f"Logged chat interaction {chat_id} with latency {latency_ms}ms")
            return audit_id
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error logging chat interaction: {e}")
            raise
    
    async def get_chat_audit(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audit information for a specific chat
        
        Args:
            chat_id: Chat session ID
            
        Returns:
            Audit information or None if not found
        """
        try:
            query = text("""
                SELECT chat_id, question, response, retrieved_docs, 
                       latency_ms, timestamp, feedback
                FROM audit_logs
                WHERE chat_id = :chat_id
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            result = await self.session.execute(query, {'chat_id': chat_id})
            row = result.fetchone()
            
            if row:
                audit_data = {
                    'chat_id': row.chat_id,
                    'question': row.question,
                    'response': row.response,
                    'retrieved_docs': row.retrieved_docs,
                    'latency_ms': row.latency_ms,
                    'timestamp': row.timestamp,
                    'feedback': row.feedback
                }
                logger.info(f"Retrieved audit data for chat {chat_id}")
                return audit_data
            else:
                logger.warning(f"No audit data found for chat {chat_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving chat audit: {e}")
            raise
    
    async def update_feedback(self, chat_id: str, feedback: str) -> bool:
        """
        Update feedback for a chat interaction
        
        Args:
            chat_id: Chat session ID
            feedback: User feedback
            
        Returns:
            True if updated, False if not found
        """
        try:
            query = text("""
                UPDATE audit_logs 
                SET feedback = :feedback
                WHERE chat_id = :chat_id
            """)
            
            result = await self.session.execute(query, {
                'chat_id': chat_id,
                'feedback': feedback
            })
            
            if result.rowcount > 0:
                await self.session.commit()
                logger.info(f"Updated feedback for chat {chat_id}")
                return True
            else:
                logger.warning(f"No audit record found for chat {chat_id}")
                return False
                
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating feedback: {e}")
            raise