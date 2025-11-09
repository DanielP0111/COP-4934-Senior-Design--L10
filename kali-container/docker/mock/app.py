from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str | None = None
    messages: List[ChatMessage]


@app.get('/v1/health')
async def health():
    return {"status": "ok"}


@app.post('/v1/chat/completions')
async def chat_completions(req: ChatRequest):
    last_user = ""
    for m in reversed(req.messages or []):
        if getattr(m, 'role', None) == 'user':
            last_user = getattr(m, 'content', '') or ''
            break

    reply_text = f"Mock reply: I received your message. (echo) -- {last_user}"

    return {
        "id": "mock-1",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": reply_text},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }
