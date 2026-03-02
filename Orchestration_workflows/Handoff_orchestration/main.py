import asyncio
import sys
from collections.abc import AsyncIterable, Iterator, Sequence
from typing import cast

from agent_framework import (
    Message,
    WorkflowEvent,
)
from dotenv import load_dotenv

from agent_framework.orchestrations import HandoffAgentUserRequest, HandoffBuilder
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

if sys.version_info >= (3, 12):
    pass  # pragma: no cover
else:
    pass  # pragma: no cover
load_dotenv()

CUSTOMER_PROMPT = "Hi, I need help with my recent order #12345. The product arrived damaged, and I’d like to request a replacement."

SCRIPTED_RESPONSES = [
    "The item arrived damaged. I'd like a replacement shipped to the same address.",
    "Great! Can you confirm the shipping cost won't be charged again?",
    "Thanks for confirming!",
]


# Agent Framework orchestration path

def _create_af_agents(client: AzureOpenAIChatClient):
    support = client.as_agent(
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
    billing = client.as_agent(
        name="BillingAgent",
        instructions=(
            "You are a billing specialist. Handle questions about invoices, payments, and account charges.\n"
            "If the request is not about billing, route back to SupportCoordinator."        ),
    )
    technical = client.as_agent(
        name="TechnicalAgent",
        instructions=(
            "You are a technical support specialist. Help with technical issues and troubleshooting.\n"
            "If the request is not about technical issues, route back to SupportCoordinator."        ),
    )
    supervisor = client.as_agent(
        name="SupervisorAgent",
        instructions=(
            "You are the support supervisor. Handle escalations and unresolved issues. Be empathetic and decisive.\n"
            "If the request is not an escalation, route back to SupportCoordinator."        ),
    )
    return support, billing, technical, supervisor


async def _drain_events(stream: AsyncIterable[WorkflowEvent]) -> list[WorkflowEvent]:
    return [event async for event in stream]


def _collect_handoff_requests(events: list[WorkflowEvent]) -> list[WorkflowEvent]:
    requests: list[WorkflowEvent] = []
    for event in events:
        if event.type == "request_info" and isinstance(event.data, HandoffAgentUserRequest):
            requests.append(event)
    return requests



def _extract_final_conversation(events: list[WorkflowEvent]) -> list[Message]:
    for event in events:
        if event.type == "output":
            data = cast(list[Message], event.data)
            return data
    return []


async def run_agent_framework_example(initial_task: str, scripted_responses: Sequence[str]) -> str:
    client = AzureOpenAIChatClient(credential=AzureCliCredential())
    triage, refund, status, returns = _create_af_agents(client)

    workflow = (
        HandoffBuilder(
            name="af_handoff",
            participants=[triage, refund, status, returns],
            termination_condition=lambda conv: sum(1 for m in conv if m.role == "user") >= 4,
        )
        .with_start_agent(triage)
        .add_handoff(triage, [refund, status, returns])
        .add_handoff(refund, [status, triage])
        .add_handoff(status, [refund, triage])
        .add_handoff(returns, [triage])
        .build()
    )

    events = await _drain_events(workflow.run(initial_task, stream=True))
    pending = _collect_handoff_requests(events)
    scripted_iter = iter(scripted_responses)

    final_events = events
    while pending:
        try:
            user_reply = next(scripted_iter)
        except StopIteration:
            user_reply = "Thanks, that's all."
        responses = {request.request_id: [Message(role="user", text=user_reply)] for request in pending}
        final_events = await _drain_events(workflow.run(stream=True, responses=responses))
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
        speaker = message.author_name or message.role
        lines.append(f"{speaker}: {text}")
    return "\n".join(lines)


# Console entry point
async def main() -> None:
    print("===== Agent Framework Handoff =====")
    af_transcript = await run_agent_framework_example(CUSTOMER_PROMPT, SCRIPTED_RESPONSES)
    print(af_transcript or "No output produced.")
    print()


if __name__ == "__main__":
    asyncio.run(main())