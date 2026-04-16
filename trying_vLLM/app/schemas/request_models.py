
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

class GenerateRequest(BaseModel):
	prompt: str
	temperature: Optional[float] = 0.7
	max_tokens: Optional[int] = 256

class GenerateResponse(BaseModel):
	response: str
	tokens_used: int
	latency_ms: float
	cost_usd: float
	model: str

class OptimizeRequest(BaseModel):
	monthly_tokens: int
	avg_input_tokens: int
	avg_output_tokens: int
	traffic_pattern: Literal["steady", "busty", "mixed"] = "steady"
	latency_target_sec: float = 1.0
	current_budget_monthly: float = 1000.0
	similarity_ratio: Optional[float] = 0.5

	@validator("monthly_tokens")
	def validate_tokens(cls, v):
		if v <= 0:
			raise ValueError("monthly_tokens must be positive")
		return v

	@validator("similarity_ratio")
	def validate_similarity(cls, v):
		if v is not None and (v < 0 or v > 1):
			raise ValueError("similarity_ratio must be between 0 and 1")
		return v

class GPUOptionResponse(BaseModel):
	cluster_id: int
	cluster_name: str
	gpu_type: str
	monthly_cost: float
	base_cost: float
	savings: float
	throughput_tokens_per_sec: float
	time_needed_sec: float
	meets_latency: bool
	latency_per_request_ms: float
	budget_feasible: bool

class OptimizeResponse(BaseModel):
	recommended: GPUOptionResponse
	all_options: List[GPUOptionResponse]
	monthly_cost: float
	potential_monthly_savings: float
	required_throughput: float
	requests_per_month: int
	optimization_summary: dict
