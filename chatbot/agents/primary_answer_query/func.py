import asyncio
from typing import TypedDict, Sequence, Annotated, List, Dict, Any
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langchain_core.documents import Document

from utils.logger import logger
from settings.gemini_client import GeminiClientService
from database.connection import get_db_session
from chatbot.vector_store import VectorStore
from chatbot.retrieval import retrieval_service

class State(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    remaining_steps: int
    query: str
    is_sensitive: bool
    retrieved_docs: list

async def get_answer_query_async(state: State):
    """
    Main function for RAG-based query answering using pgvector
    """
    logger.info(f'get_answer_query called with state: {state}')
    
    query = state.get("query", "")
    if not query:
        messages = state.get("messages", [])
        if messages and isinstance(messages[-1], HumanMessage):
            query = messages[-1].content
    
    logger.info(f'Processing query: {query}')
    
    try:
        # Step 1: Retrieve relevant documents using pgvector
        retrieved_docs = await retrieve_documents_from_pgvector(query)
        logger.info(f'Retrieved {len(retrieved_docs)} documents from pgvector')
        
        # Step 2: Synthesize answer using retrieved context
        answer = await synthesize_answer_with_llm(query, retrieved_docs)
        logger.info(f'Generated answer: {answer[:100]}...')
        
        return {
            "messages": [AIMessage(content=answer)],
            "query": query,
            "retrieved_docs": retrieved_docs
        }
        
    except Exception as e:
        logger.error(f'Error in get_answer_query: {str(e)}', exc_info=True)
        fallback_answer = "I apologize, but I'm having trouble retrieving information to answer your question. Please try again later."
        return {
            "messages": [AIMessage(content=fallback_answer)],
            "query": query,
            "retrieved_docs": []
        }

async def retrieve_documents_from_pgvector(query: str, limit: int = 5, similarity_threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Retrieve relevant documents from pgvector database
    
    Args:
        query: User query
        limit: Maximum number of documents to retrieve
        similarity_threshold: Minimum similarity score
        
    Returns:
        List of relevant documents
    """
    try:
        async with get_db_session() as session:
            vector_store = VectorStore(session)
            
            # Use the existing retrieval service
            relevant_docs = await retrieval_service.retrieve_relevant_documents(
                query=query,
                vector_store=vector_store,
                limit=limit,
                similarity_threshold=similarity_threshold
            )
            
            # Format documents for LangChain compatibility
            formatted_docs = []
            for doc in relevant_docs:
                formatted_doc = Document(
                    page_content=doc.get('content', ''),
                    metadata={
                        'id': doc.get('id'),
                        'similarity_score': doc.get('similarity_score', 0.0),
                        'created_at': str(doc.get('created_at', '')),
                        **doc.get('metadata', {})
                    }
                )
                formatted_docs.append(formatted_doc)
            
            logger.info(f'Successfully retrieved {len(formatted_docs)} documents from pgvector')
            return formatted_docs
            
    except Exception as e:
        logger.error(f'Error retrieving documents from pgvector: {str(e)}', exc_info=True)
        # Return empty list if retrieval fails
        return []

async def synthesize_answer_with_llm(query: str, documents: List[Document]) -> str:
    """
    Synthesize an answer using retrieved documents and LLM
    
    Args:
        query: User query
        documents: List of relevant documents
        
    Returns:
        Synthesized answer
    """
    try:
        if not documents:
            return "I couldn't find relevant information to answer your question. Please try rephrasing your query or provide more context."
        
        # Prepare context from retrieved documents
        context_parts = []
        for i, doc in enumerate(documents, 1):
            similarity_score = doc.metadata.get('similarity_score', 0.0)
            context_parts.append(f"Document {i} (Similarity: {similarity_score:.2f}):\n{doc.page_content}")
        
        context = "\n\n".join(context_parts)
        
        # Create synthesis prompt
        synthesis_prompt = f"""
You are an intelligent assistant helping users find information from a knowledge base.

Based on the following retrieved documents, provide a comprehensive and accurate answer to the user's question.

Context Documents:
{context}

User Question: {query}

Instructions:
1. Analyze the provided context carefully
2. Provide a clear, informative answer based on the context
3. If the context doesn't contain enough information, acknowledge this limitation
4. Include relevant details from the context when appropriate
5. Be concise but thorough in your response

Answer:
"""
        
        response = GeminiClientService().langchain_gemini.invoke(synthesis_prompt)
        synthesized_answer = response.content.strip()
        
        # Add metadata about sources
        source_info = []
        for doc in documents:
            doc_id = doc.metadata.get('id', 'unknown')
            similarity = doc.metadata.get('similarity_score', 0.0)
            source_info.append(f"Doc {doc_id[:8]} (sim: {similarity:.2f})")
        
        if source_info:
            synthesized_answer += f"\n\n*Retrieved from {len(documents)} documents: {', '.join(source_info)}*"
        
        return synthesized_answer
        
    except Exception as e:
        logger.error(f'Error in LLM synthesis: {str(e)}', exc_info=True)
        
        # Fallback to simple context-based answer
        if documents:
            context_text = "\n\n".join([doc.page_content for doc in documents[:3]])
            return f"Based on the available information:\n\n{context_text[:1000]}..."
        else:
            return "I apologize, but I couldn't generate a proper response to your question."

def get_answer_query(state: State):
    """
    Synchronous wrapper for get_answer_query_async
    """
    return asyncio.run(get_answer_query_async(state))

