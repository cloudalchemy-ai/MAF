import asyncio
from agent_framework import ChatAgent, MCPStdioTool
from agent_framework.openai import OpenAIResponsesClient


async def playwright_mcp_news_agent():
    async with (
        MCPStdioTool(
            name="PlaywrightMCPTool",
            command="npx",
            args=["@playwright/mcp@latest"],
        ) as mcp_server,
        ChatAgent(
            chat_client=OpenAIResponsesClient(),
            name="NewsReaderAgent",
            instructions="""
            You are a helpful assistant that reads news websites like a human.
            Navigate pages, open articles, and summarise content clearly.
            Focus on accuracy and clarity and use emojis.
            """
        ) as agent,
    ):
        result = await agent.run(
            """
            1. Go to BBC News.
            2. Navigate to the Technology section.
            3. Identify the top 3 headlines visible today.
            5. Produce:
               - A bullet-point summary for each article (1–2 lines each)
               - One overall trend you observe
            """,
            tools=mcp_server
        )

        print(result)

asyncio.run(playwright_mcp_news_agent())
