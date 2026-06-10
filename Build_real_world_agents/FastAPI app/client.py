"""AG-UI client that connects to the RAG agent FastAPI server."""

import asyncio
import os
from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework_ag_ui import AGUIChatClient
load_dotenv(override=True)

async def main():
    """Main client loop."""
    # AG-UI client must connect to a routable host; 0.0.0.0 is bind-only.
    server_url = (os.getenv("AGUI_SERVER_URL") or "http://127.0.0.1:8000/chat").strip()
    if "0.0.0.0" in server_url:
        server_url = server_url.replace("0.0.0.0", "127.0.0.1")
    print(f"Connecting to AG-UI server at: {server_url}\n")

    # Create AG-UI chat client
    chat_client = AGUIChatClient(endpoint=server_url)

    # Create agent with the chat client
    agent = Agent(
        name="ClientAgent",
        client=chat_client,
        instructions="You are a helpful assistant.",
    )

    # Get a thread for conversation continuity
    thread = agent.create_session()

    try:
        while True:
            # Get user input
            message = input("\nUser (:q or quit to exit): ")
            if not message.strip():
                print("Request cannot be empty.")
                continue

            if message.lower() in (":q", "quit"):
                break

            # Stream the agent response
            print("\nAssistant: ", end="", flush=True)
            async for update in agent.run(message, session=thread, stream=True):
                # Print text content as it streams
                if update.text:
                    print(f"\033[96m{update.text}\033[0m", end="", flush=True)

            print("\n")

    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n\033[91mAn error occurred: {e}\033[0m")


if __name__ == "__main__":
    asyncio.run(main())