
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

def get_env_bool(key: str, default: bool = False) -> bool:
	val = os.getenv(key)
	if val is None:
		return default
	return val.lower() in ("1", "true", "yes", "on")

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
TIMEOUT = float(os.getenv("TIMEOUT", "30"))
ENABLE_CACHE = get_env_bool("ENABLE_CACHE", False)
