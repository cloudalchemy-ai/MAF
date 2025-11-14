
import asyncio
from agent_framework import ChatAgent, MCPStdioTool
from agent_framework.openai import OpenAIChatClient

async def local_mcp_example():
    """Example using a local MCP server via stdio."""
    async with (
        MCPStdioTool( 
            #Loading Playwright MCP server via npx and using it as a Tool.
            name="PlaywrightMCPTool", 
            command="npx", 
            args=[
                "@playwright/mcp@latest"
    ],
        ) as mcp_server,
        ChatAgent(
            #OpenAI chat client for natural language communication.
            chat_client=OpenAIChatClient(), 
            name="PlaywrightMCPAgent",
            instructions="You are a helpful agent provides browser automation capabilities.",
        ) as agent,
    ):
        result = await agent.run(
            "Crawl www.example.com recursively and list all the links found for a depth of 2.", 
            tools=mcp_server
        )
        print(result)
asyncio.run(local_mcp_example())
