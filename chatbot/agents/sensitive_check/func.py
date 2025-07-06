from typing import TypedDict, Sequence, Annotated
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages

from settings.gemini_client import GeminiClientService
from utils.logger import logger

class State(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    remaining_steps: int
    query: str
    is_sensitive: bool

def sensitive_check(state: State):
    logger.info(f'sensitive_check called with state: {state}')
    
    query = state.get("query", "")
    if not query:
        messages = state.get("messages", [])
        if messages and isinstance(messages[-1], HumanMessage):
            query = messages[-1].content
    
    logger.info(f'Checking query for sensitive content: {query}')
    
    prompt = f"""
    You are a content moderator. Analyze the following query and determine if it contains:
    1. Political content (discussions about politics, political figures, government policies, etc.)
    2. Sexual content (explicit sexual topics, adult content, etc.)
    
    Query: "{query}"
    
    Respond with only "SENSITIVE" if the query contains political or sexual content, or "SAFE" if it doesn't.
    """
    
    try:
        response = GeminiClientService().langchain_gemini.invoke(prompt)
        result = response.content.strip().upper()
        
        is_sensitive = result == "SENSITIVE"
        logger.info(f'Sensitivity check result: {result}, is_sensitive: {is_sensitive}')
        
        if is_sensitive:
            rejection_message = "I apologize, but I cannot provide information on political or sexual topics. Please ask about other subjects."
            return {
                "messages": [AIMessage(content=rejection_message)],
                "is_sensitive": True,
                "query": query
            }
        else:
            return {
                "messages": state.get("messages", []),
                "is_sensitive": False,
                "query": query
            }
            
    except Exception as e:
        logger.error(f'Error in sensitive_check: {str(e)}', exc_info=True)
        return {
            "messages": [AIMessage(content="I'm sorry, there was an error processing your request.")],
            "is_sensitive": True,
            "query": query
        }