from langgraph.graph import StateGraph, START, END
from .func import State, sensitive_check
from langgraph.graph.state import CompiledStateGraph


class SensitiveCheck:
    def __init__(self):
        self.builder = StateGraph(State)

    def node(self):
        self.builder.add_node('sensitive_check', sensitive_check)

    def edge(self):
        self.builder.add_edge(START, "sensitive_check")
        self.builder.add_edge("sensitive_check", END)
        
    def __call__(self) -> CompiledStateGraph:
        self.node()
        self.edge()
        return self.builder.compile()

sensitive_check_flow = SensitiveCheck()
