
from fastapi import FastAPI

from client.agent.agent import create_agent
from client.agent.langgraph_agent import get_llm

from client.agent.langgraph_agent import get_llm, AgentState
from langchain_core.messages import HumanMessage

app = FastAPI()

@app.post("/")
async def text(query: str):
    client = get_llm()

    sys_prompt = (
    "You are a highly efficient Todo List Manager. Your goal is to help users organize "
    "tasks using the available MCP tools. "
    "\n\n"
    "OPERATIONAL RULES:\n"
    "1. **Task Management**: Use the 'mcp-todo' tools for any creation, deletion, or "
    "update of tasks. Do not hallucinate task IDs.\n"
    "2. **Calculations**: For any math or duration estimates, use the 'mcp-calculator' tools.\n"
    "3. **Time Awareness**: Always use the 'mcp-time' tool to check the current time "
    "before providing 'time remaining' updates to ensure accuracy.\n"
    "4. **Precision**: If a user is vague, ask for clarification before calling a tool.\n"
    "\n"
    "Always provide a concise summary after performing tool actions."
)
    # Pass 'client' directly to the agent
    agent_app = await create_agent(client, sys_prompt)

    inputs = {"messages": [HumanMessage(content=query)]}
    final_response = None

    async for output in agent_app.astream(inputs, stream_mode="updates"):
        for node_name, content in output.items():
            print(f"Node: {node_name}")
            if node_name == "agent": # Only capture messages from the agent node
                final_response = content["messages"][-1].content

    return {"message": final_response}


# if __name__ == "__main__":
#     asyncio.run(run_example())    