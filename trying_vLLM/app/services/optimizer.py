"""
GPU Optimizer Engine
Empirically-calibrated system that recommends the best GPU cluster
based on real-time user requirements and cost constraints.
"""

from typing import Dict, List, Any, Optional
from app.services.gpu_database import GPU_CLUSTERS
import logging

logger = logging.getLogger("optimizer")


class GPUOptimizer:
    """
    Real-time optimization engine for GPU cluster selection.
    Scales empirical data based on similarity ratio and traffic patterns.
    """

    # Traffic pattern multipliers for peak throughput
    TRAFFIC_MULTIPLIERS = {
        "steady": 1.0,
        "busty": 1.8,  # 80% peak spike
        "mixed": 1.4,  # 40% average spike
    }

    @staticmethod
    def scale_cost_by_similarity(base_cost: float, similarity_ratio: float) -> float:
        """
        Scale cost based on similarity ratio.
        Higher similarity = better optimization = lower cost.
        Formula: cost * (1 + (1 - similarity) * 0.3)
        """
        optimization_factor = 1 + (1 - similarity_ratio) * 0.3
        return base_cost * optimization_factor

    @staticmethod
    def scale_throughput_by_similarity(base_throughput: float, similarity_ratio: float) -> float:
        """
        Scale throughput based on similarity ratio.
        Higher similarity = better optimization = higher throughput.
        Formula: throughput * (0.7 + similarity * 0.3)
        """
        optimization_factor = 0.7 + similarity_ratio * 0.3
        return base_throughput * optimization_factor

    @staticmethod
    def calculate_required_throughput(
        monthly_tokens: int,
        traffic_pattern: str = "steady",
        days_per_month: int = 30,
        hours_per_day: int = 24,
    ) -> float:
        """
        Calculate required throughput (tokens/sec) from monthly token volume.
        Accounts for traffic patterns (steady/busty/mixed).
        """
        seconds_per_month = days_per_month * hours_per_day * 3600
        average_throughput = monthly_tokens / seconds_per_month
        traffic_multiplier = GPUOptimizer.TRAFFIC_MULTIPLIERS.get(traffic_pattern, 1.0)
        required_throughput = average_throughput * traffic_multiplier
        return required_throughput

    @staticmethod
    def optimize(
        monthly_tokens: int,
        avg_input_tokens: int,
        avg_output_tokens: int,
        traffic_pattern: str = "steady",
        latency_target_sec: float = 1.0,
        current_budget_monthly: float = 1000.0,
        similarity_ratio: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Run optimization pipeline to find the best GPU cluster.
        
        Returns:
        - recommended_cluster: Best cluster for requirements
        - all_options: Ranked options with costs and savings
        - monthly_cost: Projected monthly cost
        - savings_vs_baseline: Cost savings vs most expensive option
        """
        
        # Calculate required throughput
        required_throughput = GPUOptimizer.calculate_required_throughput(
            monthly_tokens, traffic_pattern
        )
        
        # Calculate average tokens per request
        avg_total_tokens = avg_input_tokens + avg_output_tokens
        
        # Estimate requests per month
        requests_per_month = monthly_tokens / avg_total_tokens if avg_total_tokens > 0 else 1
        
        # Time needed per request (budget constraint)
        time_needed_per_request = latency_target_sec
        
        # Evaluate all clusters
        options = []
        
        for cluster in GPU_CLUSTERS:
            # Scale throughput based on similarity ratio
            scaled_throughput = GPUOptimizer.scale_throughput_by_similarity(
                cluster["optimized_throughput"], 
                similarity_ratio
            )
            
            # Calculate time needed for all requests
            time_needed_sec = monthly_tokens / scaled_throughput if scaled_throughput > 0 else float('inf')
            
            # Check if meets latency target
            meets_latency = (time_needed_sec / requests_per_month) <= time_needed_per_request if requests_per_month > 0 else True
            
            # Scale cost based on similarity ratio
            scaled_cost_per_token = GPUOptimizer.scale_cost_by_similarity(
                cluster["optimized_cost_per_token"],
                similarity_ratio
            )
            
            # Calculate monthly cost
            monthly_cost = monthly_tokens * scaled_cost_per_token
            
            # Base cost (for comparison/savings)
            base_cost = monthly_tokens * cluster["base_cost_per_token"]
            
            # Calculate savings vs unoptimized
            savings = base_cost - monthly_cost
            
            options.append({
                "cluster_id": cluster["id"],
                "cluster_name": cluster["name"],
                "gpu_type": cluster["gpu_type"],
                "monthly_cost": round(monthly_cost, 2),
                "base_cost": round(base_cost, 2),
                "savings": round(savings, 2),
                "throughput_tokens_per_sec": round(scaled_throughput, 2),
                "time_needed_sec": round(time_needed_sec, 1),
                "meets_latency": meets_latency,
                "latency_per_request_ms": round((time_needed_sec / requests_per_month * 1000) if requests_per_month > 0 else 0, 2),
                "budget_feasible": monthly_cost <= current_budget_monthly,
            })
        
        # Sort by cost
        options.sort(key=lambda x: x["monthly_cost"])
        
        # Find recommended (cheapest that meets constraints)
        recommended = None
        for opt in options:
            if opt["meets_latency"] and opt["budget_feasible"]:
                recommended = opt
                break
        
        # If nothing meets constraints, pick cheapest
        if not recommended:
            recommended = options[0]
        
        # Calculate total savings vs most expensive
        max_cost = max(opt["monthly_cost"] for opt in options)
        recommended_savings = max_cost - recommended["monthly_cost"]
        
        return {
            "recommended": recommended,
            "all_options": options,
            "monthly_cost": recommended["monthly_cost"],
            "potential_monthly_savings": round(recommended_savings, 2),
            "required_throughput": round(required_throughput, 2),
            "requests_per_month": round(requests_per_month),
            "optimization_summary": {
                "monthly_tokens": monthly_tokens,
                "traffic_pattern": traffic_pattern,
                "latency_target_sec": latency_target_sec,
                "budget_limit": current_budget_monthly,
                "similarity_ratio": similarity_ratio,
            }
        }
