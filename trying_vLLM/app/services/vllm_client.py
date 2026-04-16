
import httpx
from typing import List, Dict, Any, AsyncGenerator, Optional
from app.core import config
import asyncio
import logging

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
	) -> AsyncGenerator[Dict[str, Any], None] | Dict[str, Any]:
		"""
		Calls vLLM OpenAI-compatible API for chat completions.
		If stream=True, yields chunks as they arrive.
		"""
		payload = {
			"model": self.model,
			"messages": messages,
			"stream": stream
		}
		url = f"{self.base_url}/chat/completions"
		try:
			if stream:
				async with self.client.stream("POST", url, json=payload) as response:
					async for line in response.aiter_lines():
						if line.startswith("data:"):
							chunk = line[len("data:"):].strip()
							if chunk == "[DONE]":
								break
							yield chunk
			else:
				resp = await self.client.post(url, json=payload)
				resp.raise_for_status()
				return resp.json()
		except Exception as e:
			logger.error(f"vLLM request failed: {e}")
			raise
