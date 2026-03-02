
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def main() -> None:
    from agent_framework import Agent
    from agent_framework.openai import OpenAIResponsesClient

    # AF Agent can swap in an OpenAIResponsesClient directly.
    chat_agent = Agent(
        client=OpenAIResponsesClient(),
        instructions="You are an AI Science tutor that explains complex science topics in simple terms. Use analogies and examples to make concepts easy to understand.",
        name="ScienceTutorAgent",
    )
    reply = await chat_agent.run("Explain the concept of photosynthesis in simple terms.")
    print(reply.text)


if __name__ == "__main__":
    asyncio.run(main())