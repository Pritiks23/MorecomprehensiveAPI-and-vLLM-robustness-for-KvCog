import time
from typing import Dict, Any, Tuple

class MetricsCalculator:
	"""
	Production-grade metrics calculation for LLM inference.
	Tracks latency, tokens, and estimated costs.
	"""
	
	# Pricing per 1K tokens (approximate for different models)
	MODEL_PRICING = {
		"gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
		"gpt-4": {"input": 0.03, "output": 0.06},
		"TinyLlama-1.1B-Chat-v1.0": {"input": 0.00001, "output": 0.00002},  # Self-hosted, minimal cost
		"default": {"input": 0.0001, "output": 0.0003}
	}

	@staticmethod
	def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
		"""
		Calculate estimated cost in USD for inference.
		"""
		pricing = MetricsCalculator.MODEL_PRICING.get(model, MetricsCalculator.MODEL_PRICING["default"])
		input_cost = (input_tokens / 1000) * pricing["input"]
		output_cost = (output_tokens / 1000) * pricing["output"]
		return round(input_cost + output_cost, 6)

	@staticmethod
	def estimate_tokens(text: str) -> int:
		"""
		Rough estimate of token count (approximately 4 characters per token).
		In production, use a proper tokenizer.
		"""
		return max(1, len(text) // 4)

	@staticmethod
	def track_latency(func):
		"""
		Decorator to track function execution time.
		"""
		async def wrapper(*args, **kwargs):
			start = time.time()
			result = await func(*args, **kwargs)
			latency_ms = (time.time() - start) * 1000
			return result, latency_ms
		return wrapper
