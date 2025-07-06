from typing import TypedDict, Sequence, Annotated
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from utils.logger import logger

class State(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    remaining_steps: int
    query: str
    is_sensitive: bool
    retrieved_docs: list

def postprocess(state: State):
    logger.info(f'postprocess called with state: {state}')
    
    messages = state.get("messages", [])
    query = state.get("query", "")
    is_sensitive = state.get("is_sensitive", False)
    retrieved_docs = state.get("retrieved_docs", [])
    
    logger.info(f'Processing final answer for query: {query}')
    
    if not messages:
        logger.warning("No messages to postprocess")
        return {
            "messages": [AIMessage(content="I apologize, but I couldn't generate a response to your question.")],
            "query": query
        }
    
    # Get the latest message (should be from primary_answer_query or sensitive_check)
    latest_message = messages[-1] if messages else None
    
    if not latest_message:
        logger.warning("No latest message found")
        return {
            "messages": [AIMessage(content="I apologize, but I couldn't generate a response to your question.")],
            "query": query
        }
    
    # Extract the content from the latest message
    if isinstance(latest_message, AIMessage):
        response_content = latest_message.content
    elif isinstance(latest_message, str):
        response_content = latest_message
    else:
        response_content = str(latest_message)
    
    logger.info(f'Original response: {response_content[:100]}...')
    
    # Format the final response
    final_response = format_final_response(response_content, query, is_sensitive, retrieved_docs)
    
    logger.info(f'Final formatted response: {final_response[:100]}...')
    
    return {
        "messages": [AIMessage(content=final_response)],
        "query": query,
        "is_sensitive": is_sensitive,
        "retrieved_docs": retrieved_docs
    }

def format_final_response(response: str, query: str, is_sensitive: bool, retrieved_docs: list) -> str:
    """
    Format the final response with proper structure and metadata
    """
    # If it's a sensitive content rejection, return as-is
    if is_sensitive:
        return response
    
    # Add query context if helpful
    formatted_response = response
    
    # Add source information if documents were retrieved
    if retrieved_docs and len(retrieved_docs) > 0:
        sources = []
        for doc in retrieved_docs:
            if 'source' in doc.metadata:
                sources.append(doc.metadata['source'])
        
        if sources:
            unique_sources = list(set(sources))
            source_text = f"\n\n*Sources: {', '.join(unique_sources)}*"
            formatted_response += source_text
    
    # Ensure proper formatting and readability
    formatted_response = formatted_response.strip()
    
    # Add helpful closing if appropriate
    if not is_sensitive and query:
        formatted_response += "\n\nIs there anything else you'd like to know about this topic?"
    
    return formatted_response