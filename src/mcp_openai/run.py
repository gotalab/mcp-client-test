import asyncio
import os
from mcp import StdioServerParameters
from openai_agent import OpenAIAgent
from openai_tools import OpenAIToolManager
from mcp_client import MCPClient

async def main():
    openai_api_key = os.getenv("OPENAI_API_KEY")

    model_id = "gpt-4o"
    agent = OpenAIAgent(model_id=model_id, openai_api_key=openai_api_key)
    agent.tools = OpenAIToolManager()

    agent.system_prompt = """You are a helpful assistant that can use tools to help you answer 
questions and perform tasks. If you need to use a tool, respond with a JSON containing "toolUse" field."""

    server_params = StdioServerParameters(
        command="uvx",
        args=["mcp-server-sqlite", "--db-path", "~/test.db"],
        env=None
    )

    async with MCPClient(server_params) as mcp_client:
        tools = await mcp_client.get_available_tools()
        for tool in tools:
            agent.tools.register_tool(
                name=tool.name,
                func=mcp_client.call_tool,
                description=tool.description,
                input_schema=tool.inputSchema
            )

        while True:
            try:
                user_prompt = input("\nEnter your prompt (or 'quit' to exit): ").strip()
                if user_prompt.lower() in ['quit', 'exit', 'q']:
                    break

                response = await agent.invoke_with_prompt(user_prompt)
                print("\nResponse:", response)

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
