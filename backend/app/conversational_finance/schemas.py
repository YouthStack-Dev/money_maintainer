from typing import Any
from pydantic import BaseModel, Field

class ConversationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    context: dict[str, Any] = Field(default_factory=dict)

class ConversationResponse(BaseModel):
    status: str
    intent: str
    answer: str
    data: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    follow_up: list[str] = Field(default_factory=list)
