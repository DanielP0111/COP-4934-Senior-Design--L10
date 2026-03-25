from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any, Dict
import uvicorn
from userMessageBuilder import UserMessageBuilder
from request_context import set_verified_user_id, clear_verified_user_id

app = FastAPI()

@app.get("/v1/health")
async def health():
    return {"status": "ok"}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, body: dict):
    user = request.headers.get("X-OpenWebUI-User-Id")

    # V2 security ID check
    if not user:
        return {
            "id": "error-1",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Error: Unauthorized (no user ID provided). Please log in."},
                    "finish_reason": "stop"
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }
    
    try:
        verified_user_id = int(user)
        set_verified_user_id(verified_user_id)
    except ValueError:
        return {
            "id": "error-2",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Error: Unauthorized (invalid user ID format)."},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }
    
    # V2 security: wrap orchestration in try block to allow for cleaning up user id (in case)
    try:
        message_builder = UserMessageBuilder(user, body)
        response = message_builder.getMessageResponse()
    finally:
        clear_verified_user_id()

    # Build a minimal OpenAI-style response
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
