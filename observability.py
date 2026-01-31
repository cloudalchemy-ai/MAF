# Copyright (c) Microsoft. All rights reserved.

import asyncio
import logging
import os
from random import randint
from typing import Annotated

import dotenv
from pydantic import Field

from agent_framework import ChatAgent, tool
from agent_framework.observability import (
    create_resource,
    enable_instrumentation,
    get_tracer,
)
from agent_framework.openai import OpenAIResponsesClient

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import AzureCliCredential
from azure.monitor.opentelemetry import configure_azure_monitor

from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id


# Load environment variables (AZURE_AI_PROJECT_ENDPOINT)
dotenv.load_dotenv()

logger = logging.getLogger(__name__)


# -----------------------------
# Tool definition
# -----------------------------
@tool(approval_mode="never_require")
async def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    await asyncio.sleep(randint(0, 10) / 10.0)
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return (
        f"The weather in {location} is "
        f"{conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."
    )


# -----------------------------
# Main application
# -----------------------------
async def main():
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(
            endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            credential=credential,
        ) as project_client,
    ):
        # Get Application Insights connection string from Azure AI Project
        try:
            conn_string = (
                await project_client.telemetry
                .get_application_insights_connection_string()
            )
        except Exception:
            logger.warning(
                "No Application Insights connection string found for the Azure AI Project. "
                "Please ensure Application Insights is configured for this project."
            )
            return

        # Configure Azure Monitor ONCE
        configure_azure_monitor(
            connection_string=conn_string,
            enable_live_metrics=True,
            resource=create_resource(),
            enable_performance_counters=False,
        )

        # Enable Agent Framework instrumentation
        enable_instrumentation(enable_sensitive_data=True)

        print("✅ Observability is set up. Starting Weather Agent...")

        questions = [
            "What's the weather in Amsterdam?",
            "and in Paris, and which is better?",
            "Why is the sky blue?",
        ]

        with get_tracer().start_as_current_span(
            "Weather Agent Chat",
            kind=SpanKind.CLIENT,
        ) as current_span:
            print(
                "Trace ID:",
                format_trace_id(current_span.get_span_context().trace_id),
            )

            agent = ChatAgent(
                chat_client=OpenAIResponsesClient(),
                tools=get_weather,
                name="WeatherAgent",
                instructions="You are a weather assistant.",
                id="weather-agent",
            )

            thread = agent.get_new_thread()

            for question in questions:
                print(f"\nUser: {question}")
                print(f"{agent.name}: ", end="")

                async for update in agent.run_stream(
                    question,
                    thread=thread,
                ):
                    if update.text:
                        print(update.text, end="")


if __name__ == "__main__":
    asyncio.run(main())
