from langgraph.graph import StateGraph, START, END
from .func import State
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph

from chatbot.agents.primary_answer_query.func import get_answer_query

checkpointer = InMemorySaver()

class PrimaryAnswerQuery:
    def __init__(self):
        self.builder = StateGraph(State)

    # @staticmethod
    # def routing(state: State):
    #     pass

    def node(self):
        self.builder.add_node('get_answer_query',get_answer_query)

    def edge(self):
        self.builder.add_edge(START,"get_answer_query")
        self.builder.add_edge("get_answer_query",END)
        
    def __call__(self) -> CompiledStateGraph:
        self.node()
        self.edge()
        return self.builder.compile(checkpointer=checkpointer)


primary_answer_query = PrimaryAnswerQuery()()
