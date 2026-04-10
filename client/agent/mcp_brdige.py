import asyncio
from typing import Annotated, Sequence, TypedDict, List

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import create_model

from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_classic.tools import StructuredTool



class McpBridge:
    def __init__(self, url: str = "http://localhost:8000/sse"):
        self.url = url

    async def get_langchain_tools(self) -> List[StructuredTool]:
        lc_tools = []
        async with sse_client(self.url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                mcp_tools = await session.list_tools()
                for tool in mcp_tools.tools:
                    # Call the internal helper
                    lc_tools.append(self._make_structured_tool(tool))
        return lc_tools

    def _make_structured_tool(self, mcp_tool):
        """Wraps an MCP tool call into a LangChain StructuredTool"""
        tool_name = str(mcp_tool.name)

        async def arun_wrapper(*args, **kwargs):
            # 1. Handle positional arguments (LangChain often drops a dict or string in args[0])
            if args and isinstance(args[0], dict):
                kwargs.update(args[0])
            elif args and isinstance(args[0], str):
                # Map positional string to the first expected property in the schema
                props = list(mcp_tool.inputSchema.get("properties", {}).keys())
                if props:
                    kwargs[props[0]] = args[0]

            # 2. Execute remote call
            async with sse_client(self.url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments=kwargs)

                    if hasattr(result, 'content') and result.content:
                        return result.content[0].text
                    return str(result)

        # 3. Dynamic Schema Mapping
        input_fields = {}
        properties = mcp_tool.inputSchema.get("properties", {})
        for field_name, field_info in properties.items():
            mcp_type = field_info.get("type")
            if mcp_type == "number":
                py_type = float
            elif mcp_type == "integer":
                py_type = int
            elif mcp_type == "boolean":
                py_type = bool
            else:
                py_type = str
            input_fields[field_name] = (py_type, ...)

        args_schema = create_model(f"{tool_name}Schema", **input_fields)

        return StructuredTool.from_function(
            name=tool_name,
            description=mcp_tool.description,
            coroutine=arun_wrapper,
            args_schema=args_schema
        )
