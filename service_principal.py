from azure.ai.projects.aio import AIProjectClient
from azure.identity import ClientSecretCredential
import asyncio
from dotenv import load_dotenv
import sys
import os
load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
async def main():
    credential = ClientSecretCredential(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET"),
    )

    project_client = AIProjectClient(
        endpoint="https://sree-test-agent-resource.services.ai.azure.com/api/projects/sree-test-agent",
        credential=credential,
    )

    # Example: list agents
    agents = project_client.agents
    async for agent in agents.list():
        print(agent.name)

asyncio.run(main())
