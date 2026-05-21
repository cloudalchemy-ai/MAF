import logging

import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent import root_agent as conceptualizer_agent
from agent_executor import ADKAgentExecutor
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10001)
def main(host, port):

    # Agent card (metadata)
    agent_card = AgentCard(
        name='product_conceptualizer',
        description="Generates new product ideas based on product type, target audience, and constraints.",
        url=f'http://{host}:{port}',
        version="1.0.0",
        defaultInputModes=["text", "text/plain"],
        defaultOutputModes=["text", "text/plain"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[
            AgentSkill(
                id="generate_product_concepts",
                name="Generate Product Concepts",
                description="Generates new product ideas based on product type, target audience, and constraints.",
                tags=["product_development", "innovation", "conceptualization"],
                examples=[
                    "Create an outline for a short, upbeat, and encouraging X post about learning Java",
                ],
            )
        ],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=ADKAgentExecutor(
            agent=conceptualizer_agent,
        ),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()