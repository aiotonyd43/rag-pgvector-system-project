import sys
import os
import asyncio

from google.genai import types
from typing import List
from google import genai
from typing import List

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from settings.config import settings
from utils.logger import logger
from settings.gemini_client import GeminiClientService

class EmbeddingService:
    """Service for generating text embeddings using Gemini"""
    
    def __init__(self):
        self.client = GeminiClientService().gemini_client
    
    async def embed_text(self, text: str, model: str = "text-embedding-004") -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding
        """
        try:
            # Run the blocking operation in a thread pool
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.models.embed_content(
                    model=model,
                    contents=text,
                    config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
                )
            )
            return response.embeddings[0].values
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        try:
            embeddings = []
            for text in texts:
                embedding = await self.embed_text(text)
                embeddings.append(embedding)
                await asyncio.sleep(0.3)  # Rate limiting
            
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query text
        
        Args:
            query: Query text to embed
            
        Returns:
            List of floats representing the embedding
        """
        try:
            embedding = await self.embed_text(query)

            return embedding

        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise

# Global instance
embedding_service = EmbeddingService()