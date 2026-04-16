from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.schemas.request_models import OptimizeRequest, OptimizeResponse
from app.services.optimizer import GPUOptimizer
import logging

router = APIRouter()
logger = logging.getLogger("optimizer_api")

@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_gpu_selection(body: OptimizeRequest):
	"""
	GPU Optimization Pipeline - Real-time cost optimization for AI teams.
	
	Takes user requirements and recommends the best GPU cluster for cost savings.
	
	Inputs:
	- monthly_tokens: Total tokens to process per month
	- avg_input_tokens: Average input tokens per request
	- avg_output_tokens: Average output tokens per request
	- traffic_pattern: "steady", "busty", or "mixed"
	- latency_target_sec: Maximum latency per request
	- current_budget_monthly: Monthly budget in USD
	- similarity_ratio: Model similarity (0-1, impacts optimization)
	
	Returns:
	- recommended: Best GPU cluster matching constraints
	- all_options: Ranked options with costs and savings
	- potential_monthly_savings: Cost savings vs alternatives
	"""
	try:
		result = GPUOptimizer.optimize(
			monthly_tokens=body.monthly_tokens,
			avg_input_tokens=body.avg_input_tokens,
			avg_output_tokens=body.avg_output_tokens,
			traffic_pattern=body.traffic_pattern,
			latency_target_sec=body.latency_target_sec,
			current_budget_monthly=body.current_budget_monthly,
			similarity_ratio=body.similarity_ratio or 0.5,
		)
		
		return JSONResponse(
			content=result,
			status_code=status.HTTP_200_OK
		)
		
	except Exception as e:
		logger.error(f"Optimization failed: {e}")
		return JSONResponse(
			content={"error": str(e)},
			status_code=status.HTTP_400_BAD_REQUEST
		)
