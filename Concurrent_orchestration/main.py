import asyncio
from collections.abc import Sequence
from typing import cast
from agent_framework import ChatMessage, ConcurrentBuilder, WorkflowOutputEvent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential


PROMPT = "Plan a trip to paris."


async def run_agent_framework_example(prompt: str) -> Sequence[list[ChatMessage]]:
    chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())
    # Agent 1 - Food agent
    food_agent = chat_client.create_agent(
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
    accodomation_agent = chat_client.create_agent(
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
    activities_agent = chat_client.create_agent(
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
    transport_agent = chat_client.create_agent(
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
    budget_agent = chat_client.create_agent(
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
    #defining the workflow with all 5 agents
    workflow = ConcurrentBuilder().participants([food_agent, accodomation_agent, activities_agent, transport_agent, budget_agent]).build()

    outputs: list[list[ChatMessage]] = []
    async for event in workflow.run_stream(prompt):
        if isinstance(event, WorkflowOutputEvent):
            outputs.append(cast(list[ChatMessage], event.data))

    return outputs

#printing the outputs from agent framework
def _print_agent_framework_outputs(conversations: Sequence[Sequence[ChatMessage]]) -> None:
    if not conversations:
        print("No Agent Framework output.")
        return

    print("===== Agent Framework Concurrent =====")
    for index, conversation in enumerate(conversations, start=1):
        print(f"--- Conversation {index} ---")
        for message in conversation:
            name = message.author_name or "assistant"
            print(f"[{name}] {message.text}")
        print()


async def main() -> None:
    agent_framework_outputs = await run_agent_framework_example(PROMPT)
    _print_agent_framework_outputs(agent_framework_outputs)

if __name__ == "__main__":
    asyncio.run(main())