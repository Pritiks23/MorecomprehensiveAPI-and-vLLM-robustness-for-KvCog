
import time
import logging
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.routes import completion, health

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="vLLM OpenAI-Compatible Inference API")

# Middleware for logging and request timing
class LoggingMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		start_time = time.time()
		response = await call_next(request)
		process_time = (time.time() - start_time) * 1000
		logger.info(f"{request.method} {request.url.path} completed in {process_time:.2f}ms")
		return response

app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(completion.router)
app.include_router(health.router)
