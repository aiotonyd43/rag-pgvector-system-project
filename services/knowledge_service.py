import sys
import os
from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from chatbot.vector_store import VectorStore
from chatbot.retrieval import retrieval_service
from utils.logger import logger

class KnowledgeService:
    """Service for managing knowledge base operations"""
    
    def __init__(self, session: AsyncSession):
        """Initialize knowledge service with database session"""
        self.session = session
        self.vector_store = VectorStore(session)
    
    async def update_knowledge(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update knowledge base with new documents
        
        Args:
            documents: List of documents with content and metadata
            
        Returns:
            Dictionary with processing results
        """
        try:
            processed_count = len(documents)
            failed_count = 0
            
            # Process and store documents
            success_count, document_ids = await retrieval_service.process_and_store_documents(
                documents, self.vector_store
            )
            
            result = {
                'processed_count': processed_count,
                'success_count': success_count,
                'failed_count': failed_count,
                'document_ids': document_ids
            }
            
            logger.info(f"Knowledge update completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error updating knowledge base: {e}")
            # Return error result
            return {
                'processed_count': len(documents),
                'success_count': 0,
                'failed_count': len(documents),
                'document_ids': [],
                'error': str(e)
            }
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from knowledge base
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            result = await self.vector_store.delete_document(document_id)
            
            if result:
                logger.info(f"Deleted document {document_id} from knowledge base")
            else:
                logger.warning(f"Document {document_id} not found in knowledge base")
            
            return result
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise
    
    async def get_all_documents(self) -> Dict[str, Any]:
        """
        Get all documents from knowledge base
        
        Returns:
            Dictionary with documents list and metadata
        """
        try:
            documents = await self.vector_store.get_documents()
            
            result = {
                'documents': documents,
                'total_count': len(documents)
            }
            
            logger.info(f"Retrieved {len(documents)} documents from knowledge base")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise
    
    async def search_documents(
        self, 
        query: str, 
        limit: int = 10,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search documents in knowledge base
        
        Args:
            query: Search query
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of matching documents
        """
        try:
            results = await retrieval_service.retrieve_relevant_documents(
                query=query,
                vector_store=self.vector_store,
                limit=limit,
                similarity_threshold=similarity_threshold
            )
            
            logger.info(f"Found {len(results)} documents matching query")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
