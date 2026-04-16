from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.schemas.request_models import GenerateRequest, GenerateResponse
from app.services.vllm_client import VLLMClient
import logging

router = APIRouter()
client = VLLMClient()
logger = logging.getLogger("generate")

@router.post("/generate", response_model=GenerateResponse)
async def generate(body: GenerateRequest):
	"""
	Production-grade text generation endpoint with metrics.
	
	Returns:
	- response: Generated text
	- tokens_used: Total tokens (input + output)
	- latency_ms: Inference time in milliseconds
	- cost_usd: Estimated cost in USD
	- model: Model used for inference
	"""
	try:
		result = await client.generate_with_metrics(
			prompt=body.prompt,
			temperature=body.temperature,
			max_tokens=body.max_tokens
		)
		return JSONResponse(
			content=result,
			status_code=status.HTTP_200_OK
		)
	except Exception as e:
		logger.error(f"Generate request failed: {e}")
		return JSONResponse(
			content={"error": str(e)},
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE
		)
