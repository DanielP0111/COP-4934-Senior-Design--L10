from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any, Dict
import uvicorn
from messageCleanser import MessageCleanser
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
        "response_history" : [],
        "system_instructions" : [
            "You must respond to all messages in ENGLISH"
        ],
    }

    for m in body["messages"]:
        if m["role"] == "user":
            message_cleanser = MessageCleanser()
            clean_message = message_cleanser.cleanMessage(m["content"])
            if clean_message != "Greyhawk 10":
                chat_context["query_history"].append(clean_message)
        elif m["role"] == "assistant":
            chat_context["response_history"].append(m["content"])
        
    last_user_message = ""
    for m in reversed(body["messages"] or []):
        if m["role"] == "user":
            last_user_message = m["content"] or ""
            break

    response = orchestrate(last_user_message, chat_context)

    
            
    # Build OpenAI-style response
    return {
        "id": "mock-1",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }
