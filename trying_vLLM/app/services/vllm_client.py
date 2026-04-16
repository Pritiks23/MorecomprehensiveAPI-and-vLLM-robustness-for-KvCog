
import httpx
from typing import List, Dict, Any, AsyncGenerator, Optional, Tuple
from app.core import config
from app.services.metrics import MetricsCalculator
import asyncio
import time
import logging
import random

logger = logging.getLogger("vllm_client")

class VLLMClient:
	def __init__(self):
		self.base_url = config.VLLM_BASE_URL
		self.timeout = config.TIMEOUT
		self.model = config.MODEL_NAME
		self.client = httpx.AsyncClient(timeout=self.timeout)

	async def generate_completion(
		self,
		messages: List[Dict[str, str]],
		stream: bool = False
	) -> Dict[str, Any]:
		"""
		Calls vLLM OpenAI-compatible API for chat completions (non-streaming).
		"""
		payload = {
			"model": self.model,
			"messages": messages,
			"stream": False
		}
		url = f"{self.base_url}/chat/completions"
		try:
			resp = await self.client.post(url, json=payload)
			resp.raise_for_status()
			return resp.json()
		except Exception as e:
			logger.error(f"vLLM request failed: {e}")
			raise

	async def stream_completion(
		self,
		messages: List[Dict[str, str]]
	) -> AsyncGenerator[str, None]:
		"""
		Calls vLLM OpenAI-compatible API for streaming chat completions.
		Yields chunks as they arrive.
		"""
		payload = {
			"model": self.model,
			"messages": messages,
			"stream": True
		}
		url = f"{self.base_url}/chat/completions"
		try:
			async with self.client.stream("POST", url, json=payload) as response:
				async for line in response.aiter_lines():
					if line.startswith("data:"):
						chunk = line[len("data:"):].strip()
						if chunk == "[DONE]":
							break
						yield chunk
		except Exception as e:
			logger.error(f"vLLM request failed: {e}")
			raise

	async def generate_with_metrics(
		self,
		prompt: str,
		temperature: float = 0.7,
		max_tokens: int = 256
	) -> Dict[str, Any]:
		"""
		Generate text with metrics tracking: latency, tokens, and cost.
		Production-grade endpoint for inference.
		Falls back to demo mode if vLLM is unavailable.
		"""
		start_time = time.time()
		
		try:
			# Estimate input tokens
			input_tokens = MetricsCalculator.estimate_tokens(prompt)
			
			# Create OpenAI-compatible chat message
			payload = {
				"model": self.model,
				"messages": [{"role": "user", "content": prompt}],
				"temperature": temperature,
				"max_tokens": max_tokens,
				"stream": False
			}
			
			url = f"{self.base_url}/chat/completions"
			resp = await self.client.post(url, json=payload, timeout=5.0)
			resp.raise_for_status()
			data = resp.json()
			
			# Extract response
			response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
			output_tokens = MetricsCalculator.estimate_tokens(response_text)
			
			# Calculate metrics
			latency_ms = (time.time() - start_time) * 1000
			cost_usd = MetricsCalculator.calculate_cost(self.model, input_tokens, output_tokens)
			
			return {
				"response": response_text,
				"tokens_used": input_tokens + output_tokens,
				"latency_ms": round(latency_ms, 2),
				"cost_usd": cost_usd,
				"model": self.model
			}
			
		except Exception as e:
			logger.warning(f"vLLM connection failed, using demo mode: {e}")
			# Fall back to demo mode
			return self._demo_response(prompt, start_time, temperature)

	def _demo_response(self, prompt: str, start_time: float, temperature: float) -> Dict[str, Any]:
		"""
		Generate a demo response when vLLM is unavailable.
		Simulates real inference with realistic metrics.
		"""
		demo_responses = {
			"hello": "Hello! I'm an AI assistant running on vLLM. How can I help you today?",
			"how are you": "I'm functioning perfectly! Thanks for asking. I'm ready to assist with any questions or tasks you have.",
			"what is ai": "AI (Artificial Intelligence) refers to computer systems designed to perform tasks that typically require human intelligence. This includes learning from data, recognizing patterns, and making decisions.",
			"tell a joke": "Why did the AI go to school? Because it wanted to improve its neural network! 😄",
			"default": "That's an interesting question! I'm running in demo mode since vLLM isn't connected. Connect a real vLLM backend for actual inference. How can I help you learn more about this system?"
		}

		# Match response to prompt or use default
		prompt_lower = prompt.lower()
		response_text = demo_responses["default"]
		
		for key, value in demo_responses.items():
			if key != "default" and key in prompt_lower:
				response_text = value
				break

		# Simulate realistic metrics
		input_tokens = MetricsCalculator.estimate_tokens(prompt)
		output_tokens = MetricsCalculator.estimate_tokens(response_text)
		simulated_latency = random.uniform(50, 200)  # 50-200ms
		
		latency_ms = (time.time() - start_time) * 1000 + simulated_latency
		cost_usd = MetricsCalculator.calculate_cost(self.model, input_tokens, output_tokens)

		return {
			"response": f"[DEMO MODE] {response_text}",
			"tokens_used": input_tokens + output_tokens,
			"latency_ms": round(latency_ms, 2),
			"cost_usd": cost_usd,
			"model": f"{self.model} (demo)"
		}
