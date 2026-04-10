from client.agent.mcp_brdige import McpBridge
from client.agent.langgraph_agent import get_llm, AgentState
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing import Annotated, Sequence
import asyncio

class LangGraphAgent:
    def __init__(self, llm, system_prompt, mcp_url: str,):
        self.llm = llm
        self.system_prompt = system_prompt
        self.mcp_url = mcp_url
        self.mcp_bridge = McpBridge(mcp_url)

    async def call_model(self, agent_state: AgentState):
        messages = agent_state["messages"]
        model_input = messages
        if not any(isinstance(m, SystemMessage) for m in messages):
            model_input = [SystemMessage(content=self.system_prompt)] + list(messages)
        tools = await self.mcp_bridge.get_langchain_tools()
        model_with_tools = get_llm().bind_tools(tools)
        response = await model_with_tools.ainvoke(model_input)

        return {"messages": [response]}
    
# async def create_agent(llm_client, system_prompt: str):
#         mcp_url = "http://localhost:8000/sse"
#         agent_instance = LangGraphAgent(llm_client, system_prompt, mcp_url)

#         # Define Tools
#         tools = await agent_instance.bridge.get_langchain_tools()
#         tool_node = ToolNode(tools)

#         # Initialize Graph
#         workflow = StateGraph(AgentState)

#         # Add Nodes
#         workflow.add_node("agent", agent_instance.call_model)
#         workflow.add_node("tools", tool_node)

#         # Add Edges
#         workflow.add_edge(START, "agent")

#         # Routing logic
#         def should_continue(state: AgentState):
#             last_message = state["messages"][-1]
#             if hasattr(last_message, "tool_calls") and last_message.tool_calls:

#                 return "tools"
#             return END

#         workflow.add_conditional_edges("agent", should_continue)
#         workflow.add_edge("tools", "agent")  # Loop back to LLM after tool result

#         return workflow.compile()

#     # --- 4. EXECUTION (Hardcoded Query) ---

#     def get_llm():
#         return ChatOpenAI(
#             model_name="llama-3.3-70b-versatile",
#             base_url='https://api.groq.com/openai/v1',
#             api_key='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',
#             temperature=0,
#             timeout=30,
#             max_retries=2,
#             streaming=False,
#             callbacks=None # Make sure no callback is passed
#         )

#     async def run_example():
#         # This returns a ChatOpenAI object directly
#         client = get_llm()

#         sys_prompt = "You are a helpful researcher. Use Wikipedia for facts. Calculate use mcp tools for that  "

#         # Pass 'client' directly to the agent
#         app = await create_agent(client, sys_prompt)

#         inputs = {"messages": [HumanMessage(content=  "whats the circle area radius = 10 and tell me about imran khan")]}

#         async for output in app.astream(inputs, stream_mode="updates"):
#             for node_name, content in output.items():
#                 print(f"\n--- Node: {node_name} ---")
#                 # If it's a message list, print the last one's content
#                 if "messages" in content:
#                     print(content["messages"][-1].content)
#                 else:
#                     print(content)

#     if __name__ == "__main__":
#         asyncio.run(run_example())


async def create_agent(llm_client, system_prompt: str):
    mcp_url = "http://localhost:8000/sse"
    agent_instance = LangGraphAgent(llm_client, system_prompt, mcp_url)

    # Define Tools
    tools = await agent_instance.mcp_bridge.get_langchain_tools()
    tool_node = ToolNode(tools)

    # Initialize Graph
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("agent", agent_instance.call_model)
    workflow.add_node("tools", tool_node)

    # Add Edges
    workflow.add_edge(START, "agent")

    # Routing logic
    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:

            return "tools"
        return END

    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")  # Loop back to LLM after tool result

    return workflow.compile()

# --- 4. EXECUTION (Hardcoded Query) ---

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

