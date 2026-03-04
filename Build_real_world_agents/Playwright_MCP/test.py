# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

from agent_framework import Agent, MCPStreamableHTTPTool  # Changed tool type
from agent_framework.openai import OpenAIResponsesClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

"""
Playwright MCP Example

This example demonstrates how to connect to a local Playwright MCP server.
"""

async def playwright_mcp_example() -> None:
    """Example of using Playwright MCP server via npx."""
    
    # Define the command to run the Playwright MCP server locally
    # Minimal change: No AsyncClient or headers needed
    server_params = {
        "command": "npx",
        "args": ["@playwright/mcp@latest"]
    }

    # Create MCP tool using the HTTP tool (Streamable HTTP communication)
    async with (
        MCPStreamableHTTPTool(
            name="playwright",
            description="A tool that can browse the web using Playwright",
            **server_params,
            url = 
        ) as mcp_tool,
        Agent(
            client=OpenAIResponsesClient(),
            name="Agent",
            instructions="You are a helpful assistant with web browsing capabilities.",
            tools=mcp_tool,
        ) as agent,
    ):
        query = "Search for the latest news on SpaceX and give me a summary."
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result.text}")


if __name__ == "__main__":
    asyncio.run(playwright_mcp_example())