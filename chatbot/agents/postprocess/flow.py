from langgraph.graph import StateGraph, START, END
from .func import State, postprocess
from langgraph.graph.state import CompiledStateGraph


class PostProcess:
    def __init__(self):
        self.builder = StateGraph(State)

    def node(self):
        self.builder.add_node('postprocess', postprocess)

    def edge(self):
        self.builder.add_edge(START, "postprocess")
        self.builder.add_edge("postprocess", END)
        
    def __call__(self) -> CompiledStateGraph:
        self.node()
        self.edge()
        return self.builder.compile()

postprocess_flow = PostProcess()
