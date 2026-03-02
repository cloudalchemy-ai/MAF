# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from typing import Any

from agent_framework import Message, Agent
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework.orchestrations import ConcurrentBuilder
from azure.identity import AzureCliCredential
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.azure import AzureAIProjectAgentProvider
from agent_framework.openai import OpenAIResponsesClient

"""
Sample: Concurrent fan-out/fan-in (agent-only API) with default aggregator

Build a high-level concurrent workflow using ConcurrentBuilder and three domain agents.
The default dispatcher fans out the same user prompt to all agents in parallel.
The default aggregator fans in their results and yields output containing
a list[Message] representing the concatenated conversations from all agents.

Demonstrates:
- Minimal wiring with ConcurrentBuilder(participants=[...]).build()
- Fan-out to multiple agents, fan-in aggregation of final ChatMessages
- Workflow completion when idle with no pending work

Prerequisites:
- AZURE_AI_PROJECT_ENDPOINT must be your Azure AI Foundry Agent Service (V2) project endpoint.
- Azure OpenAI access configured for AzureOpenAIResponsesClient (use az login + env vars)
- Familiarity with Workflow events (WorkflowEvent)
"""


async def main() -> None:
    # 1) Create three domain agents using AzureOpenAIResponsesClient
    chat_client = AzureOpenAIChatClient()
    credential = AzureCliCredential()

    # Agent 1 - Food agent
    food_agent = chat_client.as_agent(
        instructions=("You are a culinary and dining expert. For any travel destination, suggest:\n"
            "- Popular local dishes and specialties\n"
            "- Recommended restaurants (budget, mid-range, fine dining)\n"
            "- Street food options\n"
            "- Dining etiquette tips\n"
            "- Unique food experiences\n"
            "Provide 5-7 diverse food recommendations with brief descriptions."),
        name="FoodExpert",
    )
    # Agent 2 - Accommodation agent
    accodomation_agent = chat_client.as_agent(
        instructions=("You are a hotel and accommodation expert. For any travel destination, provide:\n"
            "- 3-4 accommodation recommendations (budget, mid-range, luxury)\n"
            "- Brief description of each option\n"
            "- Approximate price ranges\n"
            "- Location advantages\n"
            "- Booking tips\n"
            "Focus on practical, actionable accommodation advice."),
        name="AccommodationExpert",
    )

    # Agent 3 - Activities Agent
    activities_agent = await AzureAIProjectAgentProvider(credential=credential).create_agent(
        instructions = (  # Instructions for activities and attractions
            "You are a travel activities and attractions expert. For any destination, suggest:\n"
            "- Must-see attractions and landmarks\n"
            "- Unique local experiences\n"
            "- Seasonal activities\n"
            "- Day trip options\n"
            "- Cultural experiences\n"
            "Provide 5-7 diverse activity recommendations with brief descriptions."
        ),
        name = "ActivitiesExpert",
    )
    # Agent 4 - Transportation Agent
    transport_agent = await AzureAIProjectAgentProvider(credential=credential).create_agent(
        instructions = (  # Instructions for transportation options
            "You are a transportation and logistics expert. For any travel destination, provide:\n"
            "- Best ways to get there (flights, trains, buses)\n"
            "- Local transportation options (public transit, car rentals, rideshares)\n"
            "- Cost estimates\n"
            "- Travel time considerations\n"
            "- Tips for navigating the area efficiently\n"
            "Focus on practical transportation advice."
        ),
        name = "TransportExpert",
    )

    # Agent 5 - Budgeting Agent
    budget_agent = Agent (
        client = OpenAIResponsesClient(),
        instructions = (  # Instructions for budgeting and cost-saving
            "You are a travel budgeting and cost-saving expert. For any destination, provide:\n"
            "- Average daily budget estimates (accommodation, food, activities, transport)\n"
            "- Money-saving tips\n"
            "- Affordable alternatives for popular attractions\n"
            "- Best times to visit for lower costs\n"
            "- Budget-friendly accommodation and dining options\n"
            "Focus on practical budgeting advice."
        ),
        name = "BudgetExpert",
    )
    # 2) Build a concurrent workflow
    # Participants are either Agents (type of SupportsAgentRun) or Executors
    workflow = ConcurrentBuilder(participants=[food_agent, accodomation_agent, activities_agent, transport_agent, budget_agent]).build()

    # 3) Run with a single prompt and pretty-print the final combined messages
    events = await workflow.run("Plan a trip to paris.")
    outputs = events.get_outputs()

    if outputs:
        print("===== Final Aggregated Conversation (messages) =====")
        for output in outputs:
            messages: list[Message] | Any = output
            for i, msg in enumerate(messages, start=1):
                name = msg.author_name if msg.author_name else "user"
                print(f"{'-' * 60}\n\n{i:02d} [{name}]:\n{msg.text}")

    """
    Sample Output:

    ===== Final Aggregated Conversation (messages) =====
    ------------------------------------------------------------

    01 [user]:
    We are launching a new budget-friendly electric bike for urban commuters.
    ------------------------------------------------------------

    02 [researcher]:
    **Insights:**

    - **Target Demographic:** Urban commuters seeking affordable, eco-friendly transport;
        likely to include students, young professionals, and price-sensitive urban residents.
    - **Market Trends:** E-bike sales are growing globally, with increasing urbanization,
        higher fuel costs, and sustainability concerns driving adoption.
    - **Competitive Landscape:** Key competitors include brands like Rad Power Bikes, Aventon,
        Lectric, and domestic budget-focused manufacturers in North America, Europe, and Asia.
    - **Feature Expectations:** Customers expect reliability, ease-of-use, theft protection,
        lightweight design, sufficient battery range for daily city commutes (typically 25-40 miles),
        and low-maintenance components.

    **Opportunities:**

    - **First-time Buyers:** Capture newcomers to e-biking by emphasizing affordability, ease of
        operation, and cost savings vs. public transit/car ownership.
    ...
    ------------------------------------------------------------

    03 [marketer]:
    **Value Proposition:**
    "Empowering your city commute: Our new electric bike combines affordability, reliability, and
        sustainable design—helping you conquer urban journeys without breaking the bank."

    **Target Messaging:**

    *For Young Professionals:*
    ...
    ------------------------------------------------------------

    04 [legal]:
    **Constraints, Disclaimers, & Policy Concerns for Launching a Budget-Friendly Electric Bike for Urban Commuters:**

    **1. Regulatory Compliance**
    - Verify that the electric bike meets all applicable federal, state, and local regulations
        regarding e-bike classification, speed limits, power output, and safety features.
    - Ensure necessary certifications (e.g., UL certification for batteries, CE markings if sold internationally) are obtained.

    **2. Product Safety**
    - Include consumer safety warnings regarding use, battery handling, charging protocols, and age restrictions.
    ...
    """  # noqa: E501


if __name__ == "__main__":
    asyncio.run(main())