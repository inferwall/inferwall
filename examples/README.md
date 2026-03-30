# InferenceWall Integration Examples

## Available Examples

| Example | Description | Dependencies |
|---------|-------------|-------------|
| [openai_guard.py](openai_guard.py) | Wrap OpenAI API calls with input/output scanning | `inferwall openai` |
| [anthropic_guard.py](anthropic_guard.py) | Wrap Anthropic Claude API calls with scanning | `inferwall anthropic` |
| [langchain_middleware.py](langchain_middleware.py) | LangChain callback handler and wrapper function | `inferwall langchain langchain-openai` |
| [fastapi_middleware.py](fastapi_middleware.py) | FastAPI HTTP middleware for automatic scanning | `inferwall fastapi uvicorn` |

## Quick Start

```bash
pip install inferwall

# Run any example in demo mode (no API key needed)
python examples/openai_guard.py
python examples/anthropic_guard.py
python examples/langchain_middleware.py

# Run FastAPI middleware (starts server on :8001)
python examples/fastapi_middleware.py
```

## Pattern

All examples follow the same pattern:

1. **Scan input** before sending to LLM
2. **Block or flag** if threats detected
3. **Call LLM** if input is safe
4. **Scan output** before returning to user
5. **Block or redact** if sensitive data detected

```python
import inferwall

# Before LLM call
input_scan = inferwall.scan_input(user_prompt)
if input_scan.decision == "block":
    return "Request blocked"

# After LLM call
output_scan = inferwall.scan_output(llm_response)
if output_scan.decision == "block":
    return "Response redacted"
```
