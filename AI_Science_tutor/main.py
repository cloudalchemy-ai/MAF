import asyncio
import sys
from agent_framework.openai import OpenAIResponsesClient

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

"""
OpenAI Assistants Basic Example

This sample demonstrates basic usage of OpenAIAssistantsClient with automatic
assistant lifecycle management, showing both streaming and non-streaming responses as
an AI Science tutor which helps in explaining complex science topics.
"""
#Defining the non-streaming example function
async def non_streaming_example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    # Since no assistant ID is provided, the assistant will be automatically created
    # and deleted after getting a response
    async with OpenAIResponsesClient().create_agent(
        instructions="You are an AI Science tutor that explains complex science topics in simple terms. Use analogies and examples to make concepts easy to understand.",
    ) as agent:
        query = "Explain the theory of relativity."
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")

#Defining the streaming example function
async def streaming_example() -> None:
    """Example of streaming response (get results as they are generated)."""
    print("=== Streaming Response Example ===")

    # Since no assistant ID is provided, the assistant will be automatically created
    # and deleted after getting a response
    async with OpenAIResponsesClient().create_agent(
        instructions="You are an AI Science tutor that explains complex science topics in simple terms. Use analogies and examples to make concepts easy to understand.",
    ) as agent:
        query = "Explain the Pythagorean theorem."
        print(f"User: {query}")
        print("Agent: ", end="", flush=True)
        async for chunk in agent.run_stream(query):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")


async def main() -> None:
    print("=== Basic OpenAI Assistants Chat Client Agent Example ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())



