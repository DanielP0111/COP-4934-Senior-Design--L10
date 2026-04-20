from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any, Dict
import uvicorn
from userMessageBuilder import UserMessageBuilder

app = FastAPI()

@app.get("/v1/health")
async def health():
    return {"status": "ok"}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, body: dict):
    # Get user ID from API header
    user = request.headers.get("X-OpenWebUI-User-Id")

    # Build out user message with context
    message_builder = UserMessageBuilder(user, body)
    response = message_builder.getMessageResponse()
        
    # Build an OpenAI-style API response
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
