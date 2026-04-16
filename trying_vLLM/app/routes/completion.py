
from fastapi import APIRouter, Request, status
from fastapi.responses import StreamingResponse, JSONResponse
from app.schemas.request_models import ChatRequest
from app.services.vllm_client import VLLMClient
import logging
import json
import asyncio

router = APIRouter()
client = VLLMClient()
logger = logging.getLogger("completion")

@router.post("/v1/chat/completions")
async def chat_completions(request: Request, body: ChatRequest):
	stream = body.stream or False
	messages = [m.dict() for m in body.messages]

	if stream:
		async def token_stream():
			async for chunk in client.stream_completion(messages):
				# OpenAI streaming format: data: {json}\n
				yield f"data: {chunk}\n"
			yield "data: [DONE]\n"
		return StreamingResponse(token_stream(), media_type="text/event-stream")
	else:
		result = await client.generate_completion(messages)
		return JSONResponse(content=result, status_code=status.HTTP_200_OK)
