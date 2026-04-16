
# vLLM FastAPI Inference Service

## Overview

This project provides a production-ready, OpenAI-compatible inference API using FastAPI and vLLM. It supports streaming, request validation, health checks, logging, and optional Redis caching.

---

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run vLLM server:**
   ```bash
   python -m vllm.entrypoints.openai.api_server --model <MODEL_NAME>
   ```

3. **Start API (dev):**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Run with Docker:**
   ```bash
   docker build -t vllm-fastapi .
   docker run -p 3000:3000 --env-file .env vllm-fastapi
   ```

---

## API Endpoints

- `POST /v1/chat/completions` — OpenAI-compatible chat completions (streaming and non-streaming)
- `GET /health` — Health check

---

## Environment Variables

- `VLLM_BASE_URL` (default: http://localhost:8000/v1)
- `MODEL_NAME` (default: gpt-3.5-turbo)
- `TIMEOUT` (default: 30)
- `ENABLE_CACHE` (default: false)

---

## Features

- OpenAI-compatible API
- FastAPI async backend
- Streaming support
- Health checks
- Logging & request timing
- Optional Redis caching

---

## Example Request

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "stream": true
}
```

---

## Notes

- The API mirrors OpenAI's format and can be used as a drop-in replacement for local inference.
- Supports concurrent requests and efficient streaming.

---
