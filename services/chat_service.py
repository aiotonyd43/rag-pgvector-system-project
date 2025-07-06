import sys
import os
import uuid
import time
from typing import List, Dict, Any, AsyncGenerator, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from chatbot.vector_store import VectorStore
from chatbot.retrieval import retrieval_service
from chatbot.llm import llm_service
from services.audit_service import AuditService
from logs import logger

class ChatService:
    """Service for managing chat interactions"""
    
    def __init__(self, session: AsyncSession):
        """Initialize chat service with database session"""
        self.session = session
        self.vector_store = VectorStore(session)
        self.audit_service = AuditService(session)
    
    async def process_chat_query(self, query: str, chat_id: str = None) -> Dict[str, Any]:
        """
        Process a chat query and return response
        
        Args:
            query: User query
            chat_id: Optional chat ID
            
        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()
        
        try:
            # Generate chat ID if not provided
            if not chat_id:
                chat_id = str(uuid.uuid4())
            
            # Retrieve relevant documents
            retrieved_docs = await retrieval_service.retrieve_relevant_documents(
                query=query,
                vector_store=self.vector_store,
                limit=5,
                similarity_threshold=0.5
            )
            
            # Format documents for context
            context_docs = retrieval_service.format_context_documents(retrieved_docs)
            
            # Generate response
            response = await llm_service.generate_response(query, context_docs)
            
            # Calculate latency
            end_time = time.time()
            # Convert to milliseconds
            latency_ms = int((end_time - start_time) * 1000)
            
            # Log interaction
            await self.audit_service.log_chat_interaction(
                chat_id=chat_id,
                question=query,
                response=response,
                retrieved_docs=retrieved_docs,
                latency_ms=latency_ms
            )
            
            result = {
                'chat_id': chat_id,
                'response': response,
                'latency_ms': latency_ms,
                'retrieved_docs_count': len(retrieved_docs)
            }
            
            logger.info(f"Processed chat query {chat_id} in {latency_ms}ms")
            return result
            
        except Exception as e:
            # Calculate latency even for errors
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            
            logger.error(f"Error processing chat query: {e}")
            
            # Still log the failed interaction
            if not chat_id:
                chat_id = str(uuid.uuid4())
            
            try:
                await self.audit_service.log_chat_interaction(
                    chat_id=chat_id,
                    question=query,
                    response=f"Error: {str(e)}",
                    retrieved_docs=[],
                    latency_ms=latency_ms
                )
            except Exception as e:
                logger.error(f"Failed to log error interaction for chat {chat_id}: {e}")

            raise
    
    async def process_streaming_chat(
        self, 
        query: str, 
        chat_id: str = None
    ) -> AsyncGenerator[Tuple[str, Dict[str, Any]], None]:
        """
        Process a chat query with streaming response
        
        Args:
            query: User query
            chat_id: Optional chat ID
            
        Yields:
            Tuples of (response_chunk, metadata)
        """
        start_time = time.time()
        
        try:
            # Generate chat ID if not provided
            if not chat_id:
                chat_id = str(uuid.uuid4())
            
            # Retrieve relevant documents
            retrieved_docs = await retrieval_service.retrieve_relevant_documents(
                query=query,
                vector_store=self.vector_store,
                limit=5,
                similarity_threshold=0.7
            )
            
            # Format documents for context
            context_docs = retrieval_service.format_context_documents(retrieved_docs)
            
            # Send initial metadata
            metadata = {
                'chat_id': chat_id,
                'retrieved_docs_count': len(retrieved_docs),
                'status': 'streaming'
            }
            yield "", metadata
            
            # Collect full response for audit logging
            full_response = ""
            
            # Generate streaming response
            async for response_chunk in llm_service.generate_streaming_response(query, context_docs):
                full_response += response_chunk
                yield response_chunk, {'chat_id': chat_id, 'status': 'streaming'}
            
            # Calculate final latency
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            
            # Log interaction
            await self.audit_service.log_chat_interaction(
                chat_id=chat_id,
                question=query,
                response=full_response,
                retrieved_docs=retrieved_docs,
                latency_ms=latency_ms
            )
            
            # Send final metadata
            final_metadata = {
                'chat_id': chat_id,
                'latency_ms': latency_ms,
                'retrieved_docs_count': len(retrieved_docs),
                'status': 'completed'
            }
            yield "", final_metadata
            
            logger.info(f"Completed streaming chat {chat_id} in {latency_ms}ms")
            
        except Exception as e:
            # Calculate latency even for errors
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            
            logger.error(f"Error in streaming chat: {e}")
            
            # Send error metadata
            error_metadata = {
                'chat_id': chat_id or str(uuid.uuid4()),
                'latency_ms': latency_ms,
                'status': 'error',
                'error': str(e)
            }
            yield f"Error: {str(e)}", error_metadata
    
    async def get_chat_history(self, chat_id: str) -> Dict[str, Any]:
        """
        Get chat history for a specific chat ID
        
        Args:
            chat_id: Chat session ID
            
        Returns:
            Chat history data
        """
        try:
            audit_data = await self.audit_service.get_chat_audit(chat_id)
            
            if audit_data:
                logger.info(f"Retrieved chat history for {chat_id}")
                return audit_data
            else:
                logger.warning(f"No chat history found for {chat_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}")
            raise
    
    async def add_feedback(self, chat_id: str, feedback: str) -> bool:
        """
        Add feedback to a chat interaction
        
        Args:
            chat_id: Chat session ID
            feedback: User feedback
            
        Returns:
            True if feedback added successfully
        """
        try:
            result = await self.audit_service.update_feedback(chat_id, feedback)
            
            if result:
                logger.info(f"Added feedback to chat {chat_id}")
            else:
                logger.warning(f"Could not add feedback to chat {chat_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            raise