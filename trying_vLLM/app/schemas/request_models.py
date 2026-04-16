
from typing import List, Optional, Literal
from pydantic import BaseModel, validator, root_validator

ALLOWED_ROLES = {"system", "user", "assistant"}

class Message(BaseModel):
	role: str
	content: str

	@validator("role")
	def validate_role(cls, v):
		if v not in ALLOWED_ROLES:
			raise ValueError(f"role must be one of {ALLOWED_ROLES}")
		return v

class ChatRequest(BaseModel):
	messages: List[Message]
	stream: Optional[bool] = False
