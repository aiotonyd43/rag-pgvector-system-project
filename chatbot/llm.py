import sys
import os
import asyncio
from google import genai
from google.genai import types
from typing import List, Dict, Any, AsyncGenerator

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from settings.config import settings
from utils.logger import logger

class LLMService:
    """Service for interacting with Gemini LLM"""
    
    def __init__(self):
        """Initialize the LLM service"""
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        self.client = genai.Client()
        logger.info("LLM service initialized with Gemini")
    
    def _build_prompt(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Build prompt with query and retrieved context
        
        Args:
            query: User query
            context_docs: Retrieved documents for context
            
        Returns:
            Formatted prompt
        """
        if not context_docs:
            return f"""Answer the following question based on your knowledge:

Question: {query}

Please provide a helpful and accurate response."""
        
        context_text = "\n\n".join([
            f"Document {i+1}:\n{doc['content']}"
            for i, doc in enumerate(context_docs)
        ])
        
        prompt = f"""Answer the following question based on the provided context. If the context doesn't contain enough information to answer the question, say so and provide your best general knowledge response.

Context:
{context_text}

Question: {query}

Please provide a helpful and accurate response based on the context above."""
        
        return prompt
    
    def chat_generate_content(self, prompt:str):
        """
        Generate content for a chat query
        
        Args:
            prompt: User prompt

        Returns:
            Generated response
        """
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction="You are a helpful assistant.",
                    temperature=0.2,
                ),
                contents=prompt,
            )
            return response
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise
    
    def stream_chat_generate_content(self, prompt: str):
        """
        Generate streaming content for a chat query
        
        Args:
            prompt: User prompt
            
        Returns:
            Streaming response generator
        """
        try:
            response_stream = self.client.models.generate_content_stream(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction="You are a helpful assistant.",
                    temperature=0.2,
                ),
                contents=prompt,
            )
            return response_stream
            
        except Exception as e:
            logger.error(f"Error generating streaming content: {e}")
            raise

    
    async def generate_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Generate response for query with context
        
        Args:
            query: User query
            context_docs: Retrieved documents for context
            
        Returns:
            Generated response
        """
        try:
            prompt = self._build_prompt(query, context_docs)
            
            # Run the blocking operation in a thread pool
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.chat_generate_content, prompt
            )
            
            result = response.text
            logger.info(f"Generated response for query of length {len(query)}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def generate_streaming_response(
        self, 
        query: str, 
        context_docs: List[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response for query with context
        
        Args:
            query: User query
            context_docs: Retrieved documents for context
            
        Yields:
            Chunks of generated response
        """
        try:
            prompt = self._build_prompt(query, context_docs)
            
            # Run the blocking operation in a thread pool
            response_stream = await asyncio.get_event_loop().run_in_executor(
                None, self.stream_chat_generate_content, prompt
            )
            
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
            
            logger.info(f"Generated streaming response for query of length {len(query)}")
            
        except Exception as e:
            logger.error(f"Error generating streaming response: {e}")
            yield f"Error: {str(e)}"

# Global instance
llm_service = LLMService()