#!/usr/bin/env bash
# Test worker-local via proxy avec tools (format Roo minimal)
# Usage: ./scripts/test_worker_local_curl.sh

# Requête Roo-like : model worker-local + tools
curl -s -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{
    "model": "worker-local-qwen2.5-coder:14b",
    "messages": [{"role": "user", "content": "1+1=?"}],
    "stream": false,
    "tools": [
      {"type": "function", "function": {"name": "attempt_completion", "parameters": {"type": "object", "properties": {"result": {"type": "string"}}}}}
    ]
  }' 2>&1
