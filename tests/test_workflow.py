import os
import sys

from langchain_core.runnables.graph_mermaid import draw_mermaid_png

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from utils.logger import logger
from chatbot.agents.workflow import workflow

config = {"configurable": {"thread_id": "1"}}
while True:
    input_message = input(">>")
    res = workflow.invoke({"messages":[
            {"role": "human", "content": input_message},
        ],},
        config=config,
        debug=True,
    )
    logger.info(f"ChatBot Message: {res.get('messages')[-1].content}")
