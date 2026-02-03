from pydantic import BaseModel
from typing import List, Optional, Dict, Literal, Union


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class GenerateRequest(BaseModel):
    user_id: Union[int, str]
    conversation_id: Union[int, str]
    message: str
    messages: List[Message] = []
    options: Optional[Dict] = None


class GenerateResponse(BaseModel):
    assistant_message: str
    meta: Dict
