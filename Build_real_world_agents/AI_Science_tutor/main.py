# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework import tool
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from pydantic import Field

# Load environment variables from .env file
load_dotenv()

async def main() -> None:
    credential = AzureCliCredential()
    client = AzureOpenAIResponsesClient(
        project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        deployment_name=os.environ["AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"],
        credential=credential,
    )

    # creating the science tutor agent
    agent = client.as_agent(
        name="ScienceTutorAgent",
        instructions="You are an AI Science tutor that explains complex science topics in simple terms. Use analogies and examples to make concepts easy to understand.",
    )

    # #run the agent
    result = await agent.run("Explain the concept of photosynthesis in simple terms.")
    print(f"Agent: {result}")


if __name__ == "__main__":
    asyncio.run(main())