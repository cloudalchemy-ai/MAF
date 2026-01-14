import asyncio
from collections.abc import Sequence
from typing import cast
from agent_framework import ChatMessage, ConcurrentBuilder, WorkflowOutputEvent
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential
from agent_framework.openai import OpenAIAssistantsClient
from agent_framework import (
    ExecutorCompletedEvent,
    ExecutorInvokedEvent,
    WorkflowOutputEvent,
    handler,
)
from typing import Any, cast

PROMPT = "Plan a trip to paris."

def format_io_data(data: Any, detailed: bool = False) -> str:
    """Format executor I/O data for display.

    This helper formats common data types for readable output.
    Customize based on the types used in your workflow.
    """
    type_name = type(data).__name__

    if data is None:
        return "None"
    if isinstance(data, str):
        preview = data[:100] + "..." if len(data) > 100 else data
        return f"{type_name}: '{preview}'"
    if isinstance(data, ChatMessage):
        content = data.text[:150] + "..." if len(data.text) > 150 else data.text
        author = data.author_name or "assistant"
        return f"ChatMessage from '{author}': {content}"
    if isinstance(data, list):
        data_list = cast(list[Any], data)
        if len(data_list) == 0:
            return f"{type_name}: []"
        # Check if it's a list of ChatMessages
        if data_list and isinstance(data_list[0], ChatMessage):
            if detailed:
                formatted = []
                for msg in data_list:
                    author = msg.author_name or "assistant"
                    content = msg.text[:100] + "..." if len(msg.text) > 100 else msg.text
                    formatted.append(f"\n      - [{author}]: {content}")
                return f"{type_name} with {len(data_list)} messages:{''.join(formatted)}"
            return f"{type_name}: [{len(data_list)} ChatMessages]"
        # For other lists, show items with types
        if len(data_list) <= 3:
            items = [format_io_data(item) for item in data_list]
            return f"{type_name}: [{', '.join(items)}]"
        return f"{type_name}: [{len(data_list)} items]"
    return f"{type_name}: {type(data).__name__}"


async def run_agent_framework_example(prompt: str) -> Sequence[list[ChatMessage]]:
    chat_client = AzureOpenAIChatClient()
    credential = AzureCliCredential()
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
    activities_agent = AzureAIClient(credential=credential).create_agent(
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
    transport_agent = AzureAIClient(credential=credential).create_agent(
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
    budget_agent = OpenAIAssistantsClient().create_agent(
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
    #####
    print("Running workflow with executor I/O observation...\n")

    outputs: list[list[ChatMessage]] = []
    
    async for event in workflow.run_stream(prompt):
        if isinstance(event, ExecutorInvokedEvent):
            # The input message received by the executor is in event.data
            print(f"[INVOKED] {event.executor_id}")
            print(f"    Input: {format_io_data(event.data, detailed=True)}")

        elif isinstance(event, ExecutorCompletedEvent):
            # Messages sent via ctx.send_message() are in event.data
            print(f"[COMPLETED] {event.executor_id}")
            if event.data:
                print(f"    Output: {format_io_data(event.data, detailed=True)}")

        elif isinstance(event, WorkflowOutputEvent):
            print(f"\n[WORKFLOW OUTPUT] {format_io_data(event.data)}")
            outputs.append(cast(list[ChatMessage], event.data))
    
    print("\n" + "="*80)
    ########
    return outputs

#printing the outputs from agent framework
def _print_agent_framework_outputs(conversations: Sequence[Sequence[ChatMessage]]) -> None:
    if not conversations:
        print("No Agent Framework output.")
        return

    print("\n===== FINAL AGGREGATED RESULTS =====")
    print(f"Total conversations: {len(conversations)}\n")
    
    for index, conversation in enumerate(conversations, start=1):
        print(f"\n{'='*80}")
        print(f"Conversation {index} ({len(conversation)} messages)")
        print("="*80)
        for msg_idx, message in enumerate(conversation, start=1):
            name = message.author_name or "assistant"
            print(f"\n[Message {msg_idx} - {name}]")
            print("-" * 80)
            print(message.text)
        print()


async def main() -> None:
    agent_framework_outputs = await run_agent_framework_example(PROMPT)
    _print_agent_framework_outputs(agent_framework_outputs)

if __name__ == "__main__":
    asyncio.run(main())