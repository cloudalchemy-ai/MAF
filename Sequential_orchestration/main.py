# Copyright (c) Microsoft. All rights reserved.

"""Side-by-side sequential orchestrations for Agent Framework and Semantic Kernel."""

import asyncio
from collections.abc import Sequence
from typing import cast

from agent_framework import ChatMessage, Role, SequentialBuilder, WorkflowOutputEvent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential


PROMPT = "Just finished my morning workout. Feeling good about staying consistent with my fitness routine. It's been 3 weeks now and I can see some progress. Anyone else trying to stay motivated?"

async def get_social_media_agents(prompt: str) -> list[ChatMessage]:
    """
    Define three agents for social media post optimization:
    1. AnalyzerAgent: Analyzes the original post for tone, engagement factors, and issues
    2. OptimizerAgent: Creates an improved version based on the analysis
    3. ReviewerAgent: Final review and polish for maximum engagement
    """
    chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())
    # Agent 1-Analyzer Agent
    analyzer_agent = chat_client.create_agent(
        instructions=("You are a social media analyst. Given a social media post, analyze and identify:\n"
            "- Current tone and style\n"
            "- Engagement potential (hashtags, call-to-action, emotional appeal)\n"
            "- Target audience\n"
            "- Areas for improvement\n"
            "- Missing elements (emojis, hashtags, etc.)\n\n"
            "Provide a structured analysis with specific recommendations."),
        name="AnalyzerAgent",
    )
    # Agent 2-Optimizer Agent
    optimizer_agent = chat_client.create_agent(
        instructions=("You are a social media content optimizer. Based on the analysis provided, "
            "create an improved version of the original social media post that:\n"
            "- Enhances engagement potential\n"
            "- Improves clarity and impact\n"
            "- Adds appropriate hashtags and emojis\n"
            "- Includes a clear call-to-action\n"
            "- Maintains authenticity\n\n"
            "Output only the optimized post content."),
        name="OptimizerAgent",
    )
    # Agent 3-Reviewer Agent
    reviewer_agent = chat_client.create_agent(
        instructions=("You are a social media content reviewer. Review the optimized post and make final improvements:\n"
            "- Ensure perfect grammar and spelling\n"
            "- Optimize hashtag placement and relevance\n"
            "- Balance emoji usage (not too many, not too few)\n"
            "- Ensure the call-to-action is compelling\n"
            "- Make sure the post fits platform character limits\n\n"
            "Output the final, polished social media post."),
        name="ReviewerAgent",
    )

    workflow = SequentialBuilder().participants([analyzer_agent, optimizer_agent, reviewer_agent]).build()

    conversation_outputs: list[list[ChatMessage]] = []
    async for event in workflow.run_stream(prompt):
        if isinstance(event, WorkflowOutputEvent):
            conversation_outputs.append(cast(list[ChatMessage], event.data))

    return conversation_outputs[-1] if conversation_outputs else []



def _format_conversation(conversation: list[ChatMessage]) -> None:
    if not conversation:
        print("No Agent Framework output.")
        return

    print("===== Agent Framework Sequential =====")
    for index, message in enumerate(conversation, start=1):
        name = message.author_name or ("assistant" if message.role == Role.ASSISTANT else "user")
        print(f"{'-' * 60}\n{index:02d} [{name}]\n{message.text}")
    print()


async def main() -> None:
    conversation = await get_social_media_agents(PROMPT)
    _format_conversation(conversation)


if __name__ == "__main__":
    asyncio.run(main())