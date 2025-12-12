from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    sources: List