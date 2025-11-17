from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any, Dict
import uvicorn
from orchestration import orchestrate

app = FastAPI()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage]

@app.get("/v1/health")
async def health():
    return {"status": "ok"}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, body: dict):
    # Simple mock: echo the last message whose role == 'user'.
    # Ignore assistant/tool messages to avoid echo-amplification when used as a loopback.

    user = request.headers.get("X-OpenWebUI-User-Id")

    chat_context = f"--CONTEXT--\nTHIS IS A CHAT WITH USER ID {user}\n"

    for m in body["messages"]:
        chat_context += f"{m["role"]}: {m["content"]}\n"

    chat_context += "--CONTEXT--\n"

    last_user_message = ""
    for m in reversed(body["messages"] or []):
        # messages are pydantic models; use getattr to be defensive
        if m["role"] == "user":
            last_user_message = m["content"] or ""
            break
            
    chat_context += f"USER MESSAGE (USER ID: {user}): {last_user_message}"

    reply = ""
    chat = orchestrate(chat_context)
    for response in chat.chat_history:
        if response["role"] == "user" and response["name"] != "user":
            reply = response["content"]
            break
        if reply == "":
            reply = response["content"]
    # Build a minimal OpenAI-style response
    return {
        "id": "mock-1",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": reply},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }
