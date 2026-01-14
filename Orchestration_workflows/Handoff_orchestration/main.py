import asyncio
import sys
from collections.abc import AsyncIterable, Iterator, Sequence
from typing import cast

from agent_framework import (
    ChatMessage,
    HandoffBuilder,
    HandoffUserInputRequest,
    RequestInfoEvent,
    WorkflowEvent,
    WorkflowOutputEvent,
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


CUSTOMER_PROMPT = "Hi, I need help with my recent order #12345. The product arrived damaged, and I’d like to request a replacement."

SCRIPTED_RESPONSES = [
    "Yes, the item was completely damaged when it arrived. Please arrange a replacement to be shipped to the same address.",
    "Thanks! Can you tell me when the replacement will be delivered?",
    "I just want to make sure I won’t be charged again for shipping or replacement costs.",
    "Actually, the last time I contacted support about this, it wasn’t resolved properly. Could I please speak with a supervisor?",
    "Thank you for your help!"
]


######################################################################
# Agent Framework orchestration path
######################################################################


def _create_af_agents(client: AzureOpenAIChatClient):
    support = client.create_agent(
        name="SupportCoordinator",
        instructions=(
            "You are the main customer support coordinator. Greet the customer and understand their issue.\n"
            "Route the conversation to the right specialist:\n"
            "BillingAgent: For billing and payment issues\n"
            "TechnicalAgent: For technical problems\n"
            "SupervisorAgent: For escalations or unresolved issues\n"
            "Always be polite and helpful. If unsure, ask clarifying questions."
        ),
    )
    billing = client.create_agent(
        name="BillingAgent",
        instructions=(
            "You are a billing specialist. Handle questions about invoices, payments, and account charges.\n"
            "If the request is not about billing, route back to SupportCoordinator."        ),
    )
    technical = client.create_agent(
        name="TechnicalAgent",
        instructions=(
            "You are a technical support specialist. Help with technical issues and troubleshooting.\n"
            "If the request is not about technical issues, route back to SupportCoordinator."        ),
    )
    supervisor = client.create_agent(
        name="SupervisorAgent",
        instructions=(
            "You are the support supervisor. Handle escalations and unresolved issues. Be empathetic and decisive.\n"
            "If the request is not an escalation, route back to SupportCoordinator."        ),
    )
    return support, billing, technical, supervisor


async def _drain_events(stream: AsyncIterable[WorkflowEvent]) -> list[WorkflowEvent]:
    return [event async for event in stream]


def _collect_handoff_requests(events: list[WorkflowEvent]) -> list[RequestInfoEvent]:
    requests: list[RequestInfoEvent] = []
    for event in events:
        if isinstance(event, RequestInfoEvent) and isinstance(event.data, HandoffUserInputRequest):
            requests.append(event)
    return requests


def _extract_final_conversation(events: list[WorkflowEvent]) -> list[ChatMessage]:
    for event in events:
        if isinstance(event, WorkflowOutputEvent):
            data = cast(list[ChatMessage], event.data)
            return data
    return []


async def run_agent_framework_example(initial_task: str, scripted_responses: Sequence[str]) -> str:
    client = AzureOpenAIChatClient(credential=AzureCliCredential())
    support, billing, technical, supervisor = _create_af_agents(client)

    workflow = (
        HandoffBuilder(name="af_handoff_migration", participants=[support, billing, technical, supervisor], )
        .set_coordinator(support)
        .add_handoff(support, [billing, technical, supervisor])
        .add_handoff(billing, [technical, support])
        .add_handoff(technical, [billing, support])
        .add_handoff(supervisor, support)
        .build()
    )

    events = await _drain_events(workflow.run_stream(initial_task))
    pending = _collect_handoff_requests(events)
    scripted_iter = iter(scripted_responses)

    final_events = events
    while pending:
        try:
            user_reply = next(scripted_iter)
        except StopIteration:
            user_reply = "Thanks, that's all."
        responses = {request.request_id: user_reply for request in pending}
        final_events = await _drain_events(workflow.send_responses_streaming(responses))
        pending = _collect_handoff_requests(final_events)

    conversation = _extract_final_conversation(final_events)
    if not conversation:
        return ""

    # Render final transcript succinctly.
    lines = []
    for message in conversation:
        text = message.text or ""
        if not text.strip():
            continue
        speaker = message.author_name or message.role.value
        lines.append(f"{speaker}: {text}")
    return "\n".join(lines)


######################################################################
# Console entry point
######################################################################


async def main() -> None:
    print("===== Agent Framework Handoff =====")
    af_transcript = await run_agent_framework_example(CUSTOMER_PROMPT, SCRIPTED_RESPONSES)
    print(af_transcript or "No output produced.")
    print()


if __name__ == "__main__":
    asyncio.run(main())