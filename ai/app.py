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
    user = request.headers.get("X-OpenWebUI-User-Id")
    
    chat_context = {
        "user_name" : user,
        "query_history" : [],
        "response_history" : []
    }

    chat_content = []

    for m in body["messages"]:
        if m["role"] == "user":
            chat_context["query_history"].append(m["content"])
        elif m["role"] == "assistant":
            chat_context["response_history"].append(m["content"])
        chat_content.append({"role" : m["role"], "content" : m["content"]})
        
    last_user_message = ""
    for m in reversed(body["messages"] or []):
        if m["role"] == "user":
            last_user_message = m["content"] or ""
            break

    chat = orchestrate(last_user_message, chat_context)

    reply = ""
        
    for response in chat.chat_history:
        if response["role"] == "user" and response["name"] != "user":
            reply = response["content"]
            break
        if reply == "":
            reply = response["content"]
            
    # Build OpenAI-style response
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
