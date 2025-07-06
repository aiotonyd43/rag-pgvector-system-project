import sys
import os
import uuid
import json
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, delete

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from logs import logger
from utils.helper import get_current_vietnam_datetime

class VectorStore:
    """PostgreSQL + pgvector implementation for vector storage"""
    
    def __init__(self, session: AsyncSession):
        """Initialize vector store with database session"""
        self.session = session
    
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """
        Convert metadata dict to PostgreSQL JSONB format
        
        Args:
            metadata: Dictionary of metadata
            
        Returns:
            JSON string formatted for PostgreSQL JSONB type
        """
        if isinstance(metadata, dict):
            return json.dumps(metadata, ensure_ascii=False)
        else:
            return json.dumps({}) if metadata is None else str(metadata)
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple documents to the vector store
        
        Args:
            documents: List of documents with content, embedding, and metadata
            
        Returns:
            List of document IDs
        """
        try:
            document_ids = []
            
            for doc in documents:
                doc_id = str(uuid.uuid4())

                embedding_str = '[' + ','.join(map(str, doc['embedding'])) + ']'
                
                # Insert document with embedding
                query = text("""
                    INSERT INTO documents (id, content, embedding, metadata, created_at)
                    VALUES (:id, :content, :embedding, :metadata, :created_at)
                """)

                insert_data = {
                    'id': doc_id,
                    'content': doc['content'],
                    'embedding': embedding_str,
                    'metadata': self._format_metadata(doc.get('metadata', {})),
                    'created_at': get_current_vietnam_datetime()
                }
                
                await self.session.execute(query, insert_data)
                
                document_ids.append(doc_id)
            
            await self.session.commit()
            logger.info(f"Added {len(documents)} documents to vector store")
            return document_ids
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document by ID
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            query = text("DELETE FROM documents WHERE id = :doc_id")
            result = await self.session.execute(query, {'doc_id': document_id})
            
            if result.rowcount > 0:
                await self.session.commit()
                logger.info(f"Deleted document {document_id}")
                return True
            else:
                logger.warning(f"Document {document_id} not found")
                return False
                
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting document {document_id}: {e}")
            raise
    
    async def get_documents(self) -> List[Dict[str, Any]]:
        """
        Get all documents metadata
        
        Returns:
            List of document metadata
        """
        try:
            query = text("""
                SELECT id, content, metadata, created_at,
                       LENGTH(content) as size
                FROM documents
                ORDER BY created_at DESC
            """)
            
            result = await self.session.execute(query)
            rows = result.fetchall()
            
            documents = []
            for row in rows:
                documents.append({
                    'id': str(row.id),
                    'size': row.size,
                    'created_at': row.created_at,
                    'metadata': row.metadata
                })
            
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise
    
    async def similarity_search(
        self, 
        query_embedding: List[float], 
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search using cosine similarity
        
        Args:
            query_embedding: Query vector
            limit: Number of results to return
            threshold: Similarity threshold
            
        Returns:
            List of similar documents with scores
        """
        try:
            # Convert embedding to string format for PostgreSQL
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # Cosine similarity have value between 0 to 2
            query = text("""
                SELECT id, content, metadata, created_at,
                       1 - (embedding <=> :query_embedding) as similarity_score
                FROM documents
                WHERE 1 - (embedding <=> :query_embedding) > :threshold
                ORDER BY embedding <=> :query_embedding
                LIMIT :limit
            """)
            
            result = await self.session.execute(query, {
                'query_embedding': embedding_str,
                'threshold': threshold,
                'limit': limit
            })
            
            rows = result.fetchall()
            
            documents = []
            for row in rows:
                documents.append({
                    'id': str(row.id),
                    'content': row.content,
                    'metadata': row.metadata,
                    'similarity_score': float(row.similarity_score),
                    'created_at': row.created_at
                })
            
            logger.info(f"Found {len(documents)} similar documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            raise
    
    async def update_document(self, document_id: str, content: str, embedding: List[float], metadata: Dict[str, Any] = None) -> bool:
        """
        Update an existing document
        
        Args:
            document_id: ID of document to update
            content: New content
            embedding: New embedding
            metadata: New metadata
            
        Returns:
            True if updated, False if not found
        """
        try:
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            query = text("""
                UPDATE documents 
                SET content = :content, 
                    embedding = :embedding, 
                    metadata = :metadata,
                    updated_at = :updated_at
                WHERE id = :doc_id
            """)

            update_data = {
                'doc_id': document_id,
                'content': content,
                'embedding': embedding_str,
                'metadata': self._format_metadata(metadata),
                'updated_at': get_current_vietnam_datetime()
            }
            
            result = await self.session.execute(query, update_data)
            
            if result.rowcount > 0:
                await self.session.commit()
                logger.info(f"Updated document {document_id}")
                return True
            else:
                logger.warning(f"Document {document_id} not found for update")
                return False
                
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating document {document_id}: {e}")
            raise