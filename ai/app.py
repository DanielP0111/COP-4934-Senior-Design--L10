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
    # V2 security: wrap orchestration in try block to allow for cleaning up user id (in case)

    try:
        chat = orchestrate(chat_context)
        for response in chat.chat_history:
            if response["role"] == "user" and response["name"] != "user":
                reply = response["content"]
                break
            if reply == "":
                reply = response["content"]
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
