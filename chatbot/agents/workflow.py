from typing import TypedDict
from typing import Sequence, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from utils.logger import logger
from langgraph.graph import START, END
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from chatbot.agents.primary_answer_query.flow import primary_answer_query
from chatbot.agents.sensitive_check.flow import sensitive_check
from chatbot.agents.postprocess.flow import postprocess

class State(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    remaining_steps: int
    query: str
    is_sensitive: bool
    retrieved_docs: list

checkpointer = InMemorySaver()

class Workflow:
    def __init__(self):
        self.builder = StateGraph(State)

    @staticmethod
    def routing(state):
        logger.info(f'Routing called with state: {state}')
        
        # Check if content is sensitive
        is_sensitive = state.get("is_sensitive", False)
        if is_sensitive:
            logger.info("Content is sensitive, routing to postprocess")
            return "postprocess"
        
        # If not sensitive, route to primary_answer_query
        messages = state.get("messages", [])
        if not messages:
            logger.error("State Message is empty", exc_info=True)
            return "postprocess"
        
        logger.info("Content is safe, routing to primary_answer_query")
        return "primary_answer_query"


    def node(self):
        self.builder.add_node("sensitive_check", sensitive_check)
        self.builder.add_node("primary_answer_query", primary_answer_query)
        self.builder.add_node("postprocess", postprocess)

    def edge(self):
        self.builder.add_edge(START, "sensitive_check")
        self.builder.add_conditional_edges(
            "sensitive_check",
            self.routing,
            {
                "primary_answer_query": "primary_answer_query",
                "postprocess": "postprocess"
            },
        )
        self.builder.add_edge("primary_answer_query", "postprocess")
        self.builder.add_edge("postprocess", END)

    def __call__(self) -> CompiledStateGraph:
        self.node()
        self.edge()
        return self.builder.compile(checkpointer=checkpointer)

workflow = Workflow()()
