"""Async streaming client for Anthropic Claude."""
import anthropic

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024


async def stream_claude(
    api_key: str,
    messages: list[dict],
    system: str = "",
    temperature: float = 0.7,
    max_tokens: int = MAX_TOKENS,
):
    """
    Yield text chunks from Claude's streaming messages API.
    Raises anthropic.AuthenticationError if the key is invalid.
    """
    client = anthropic.AsyncAnthropic(api_key=api_key)
    kwargs = dict(
        model=MODEL,
        max_tokens=max_tokens,
        messages=messages,
        temperature=temperature,
    )
    if system:
        kwargs["system"] = system

    async with client.messages.stream(**kwargs) as stream:
        async for text in stream.text_stream:
            yield text
