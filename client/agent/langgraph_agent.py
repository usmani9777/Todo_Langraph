from typing import Annotated, Sequence
from langchain_openai import ChatOpenAI
from typing import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# def get_llm():
#     return ChatOpenAI(
#         model_name="llama-3.3-70b-versatile",
#         base_url='https://api.groq.com/openai/v1',
#         api_key='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',
#         temperature=0,
#         timeout=30,
#         max_retries=2,
#         streaming=False,
#         callbacks=None # Make sure no callback is passed
#     )

def get_llm():
    return ChatOpenAI(
        model_name="llama-3.3-70b-versatile",
        base_url='https://api.groq.com/openai/v1',
        api_key='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',
        temperature=0,
        timeout=30,
        max_retries=2,
        streaming=False,
        callbacks=None # Make sure no callback is passed
    )

class AgentState(TypedDict):
   messages: Annotated[Sequence[BaseMessage], add_messages]