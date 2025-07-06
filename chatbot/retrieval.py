import sys
import os
from typing import List, Dict, Any, Tuple
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from settings.config import settings
from chatbot.embeddings import embedding_service
from chatbot.vector_store import VectorStore
from utils.logger import logger

class RetrievalService:
    """Service for document retrieval and RAG operations"""
    
    def __init__(self):
        """Initialize the retrieval service"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        logger.info("Retrieval service initialized")
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Split documents into chunks
        
        Args:
            documents: List of documents with content and metadata
            
        Returns:
            List of document chunks
        """
        try:
            chunks = []
            
            for doc in documents:
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                
                # Split content into chunks
                text_chunks = self.text_splitter.split_text(content)
                
                for i, chunk in enumerate(text_chunks):
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update({
                        'chunk_index': i,
                        'total_chunks': len(text_chunks),
                        'original_doc_length': len(content)
                    })
                    
                    chunks.append({
                        'content': chunk,
                        'metadata': chunk_metadata
                    })
            
            logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking documents: {e}")
            raise
    
    async def process_and_store_documents(
        self, 
        documents: List[Dict[str, Any]], 
        vector_store: VectorStore
    ) -> Tuple[int, List[str]]:
        """
        Process documents and store them in vector store
        
        Args:
            documents: List of documents to process
            vector_store: Vector store instance
            
        Returns:
            Tuple of (success_count, document_ids)
        """
        try:
            # Chunk documents
            chunks = self.chunk_documents(documents)
            
            # Generate embeddings for chunks
            contents = [chunk['content'] for chunk in chunks]
            embeddings = await embedding_service.embed_texts(contents)
            
            # Prepare documents for storage
            storage_docs = []
            for chunk, embedding in zip(chunks, embeddings):
                storage_docs.append({
                    'content': chunk['content'],
                    'embedding': embedding,
                    'metadata': chunk['metadata']
                })
            
            # Store in vector store
            document_ids = await vector_store.add_documents(storage_docs)
            
            logger.info(f"Processed and stored {len(chunks)} document chunks")
            return len(chunks), document_ids
            
        except Exception as e:
            logger.error(f"Error processing and storing documents: {e}")
            raise
    
    async def retrieve_relevant_documents(
        self, 
        query: str, 
        vector_store: VectorStore,
        limit: int = 5,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User query
            vector_store: Vector store instance
            limit: Maximum number of documents to retrieve
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of relevant documents
        """
        try:
            # Generate query embedding
            query_embedding = await embedding_service.embed_query(query)
            
            # Perform similarity search
            similar_docs = await vector_store.similarity_search(
                query_embedding=query_embedding,
                limit=limit,
                threshold=similarity_threshold
            )
            
            logger.info(f"Retrieved {len(similar_docs)} relevant documents for query")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error retrieving relevant documents: {e}")
            raise
    
    def format_context_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format retrieved documents for context
        
        Args:
            documents: Retrieved documents
            
        Returns:
            Formatted documents for LLM context
        """
        try:
            formatted_docs = []
            
            for doc in documents:
                formatted_doc = {
                    'id': doc.get('id'),
                    'content': doc.get('content', ''),
                    'similarity_score': doc.get('similarity_score', 0.0),
                    'metadata': doc.get('metadata', {})
                }
                formatted_docs.append(formatted_doc)
            
            # Sort by similarity score (highest first)
            formatted_docs.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            logger.debug(f"Formatted {len(formatted_docs)} context documents")
            return formatted_docs
            
        except Exception as e:
            logger.error(f"Error formatting context documents: {e}")
            raise

# Global instance
retrieval_service = RetrievalService()