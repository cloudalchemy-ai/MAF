from pathlib import Path

import chromadb
from dotenv import load_dotenv
from agent_framework import Agent, ContextProvider, Message
from agent_framework.foundry import FoundryChatClient
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint
from azure.identity import DefaultAzureCredential
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
POLICY_DOCUMENT = BASE_DIR / "company_policy.md"

# ── RAG Context Provider (retrieve only — as minimal as it gets) ───

class RAGProvider(ContextProvider):
    def __init__(self, col):
        super().__init__("rag")
        self._col = col

    async def before_run(self, *, agent, session, context, state):
        query = " ".join(m.text for m in context.input_messages if m and m.text)
        results = self._col.query(query_texts=[query], n_results=3, include=["documents"])
        context.extend_messages(self.source_id, [
            Message(role="user", contents=["\n---\n".join(results["documents"][0])])
        ])


def build_agent() -> Agent:
    if not POLICY_DOCUMENT.exists():
        raise FileNotFoundError(f"Policy document not found at: {POLICY_DOCUMENT}")

    col = chromadb.Client().get_or_create_collection("docs")
    text = POLICY_DOCUMENT.read_text(encoding="utf-8")
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    col.upsert(ids=[f"p::{i}" for i in range(len(chunks))], documents=chunks)

    return Agent(
        client=FoundryChatClient(credential=DefaultAzureCredential()),
        name="rag-agent",
        instructions="Answer ONLY from the provided context. Say 'I don't know' if not covered.",
        context_providers=[RAGProvider(col)],
    )


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


agent = build_agent()
app = FastAPI(title="MAF RAG FastAPI", version="1.0.0")

# AG-UI SSE endpoint expected by AGUIChatClient.
add_agent_framework_fastapi_endpoint(app=app, agent=agent, path="/chat")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat-json", response_model=ChatResponse)
async def chat_json(request: ChatRequest) -> ChatResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question cannot be empty")

    answer = await agent.run(question)
    return ChatResponse(answer=str(answer))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)