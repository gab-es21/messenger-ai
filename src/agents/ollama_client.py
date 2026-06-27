"""Async streaming client for Ollama's chat API."""
import json
import httpx

CHAT_PATH = "/api/chat"
TIMEOUT = 120.0


async def stream_ollama(
    base_url: str,
    model: str,
    messages: list[dict],
    temperature: float = 0.7,
):
    """
    Yield text chunks from Ollama's streaming chat endpoint.
    Raises httpx.ConnectError if the server is unreachable.
    """
    url = base_url.rstrip("/") + CHAT_PATH
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": temperature},
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        async with client.stream("POST", url, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    text = chunk.get("message", {}).get("content", "")
                    if text:
                        yield text
                    if chunk.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
