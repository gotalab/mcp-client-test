from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Any, List, Optional
import asyncio

class MCPClient:
    def __init__(self, server_params: StdioServerParameters):
        self.server_params: StdioServerParameters = server_params
        self.session: Optional[ClientSession] = None
        self._client = None
        
    async def __aenter__(self) -> 'MCPClient':
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def connect(self):
        self._client = stdio_client(self.server_params)
        self.read, self.write = await self._client.__aenter__()
        session = ClientSession(self.read, self.write)
        self.session = await session.__aenter__()
        await self.session.initialize()

    async def get_available_tools(self) -> List[Any]:
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        tools = await self.session.list_tools()
        _, tools_list = tools
        _, tools_list = tools_list
        return tools_list

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        result = await self.session.call_tool(tool_name, arguments=arguments)
        return result
