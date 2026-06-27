"""Runs one agent's turn: builds prompt, picks client, yields text chunks."""
from agents.history import build_messages
from utils.logger import get_logger

log = get_logger(__name__)

_LENGTH_HINT = {
    "short":  "Reply in 1-2 sentences only. Be punchy.",
    "medium": "Reply in one short paragraph.",
    "long":   "Reply in up to 3 paragraphs. Be thorough.",
}


def _system_prompt(agent: dict) -> str:
    name    = agent["name"]
    persona = agent.get("persona", "").strip()
    length  = _LENGTH_HINT.get(agent.get("response_length", "medium"), "")
    parts = [
        f"You are {name}, a participant in a multi-agent brainstorming session.",
        persona,
        length,
        (
            "Rules: stay in character; be direct; never say 'As an AI'; "
            "do not greet or introduce yourself unless asked."
        ),
    ]
    return "\n\n".join(p for p in parts if p)


async def run_agent_turn(agent: dict, message_log: list[dict], global_cfg: dict):
    """
    Async generator — yields text chunks for one agent's reply.

    agent:       one item from SettingsStore.agents
    message_log: ChatWindow._message_log (treat as read-only)
    global_cfg:  SettingsStore.global_cfg
    """
    messages = build_messages(message_log, agent["id"])
    if not messages:
        return

    system      = _system_prompt(agent)
    temperature = float(agent.get("temperature", 0.7))
    source      = agent.get("source", "ollama")

    try:
        if source == "claude":
            api_key = global_cfg.get("claude_api_key", "").strip()
            if not api_key:
                yield "[Error: Claude API key not configured — go to Settings → Global]"
                return
            from agents.claude_client import stream_claude
            async for chunk in stream_claude(
                api_key=api_key,
                messages=messages,
                system=system,
                temperature=temperature,
            ):
                yield chunk

        else:  # ollama
            base_url = global_cfg.get("ollama_url", "http://localhost:11434").rstrip("/")
            model    = global_cfg.get("ollama_model", "zephyr:7b-alpha-q4_K_M")
            # Zephyr and most GGUF models accept a system role at position 0
            full_messages = [{"role": "system", "content": system}] + messages
            from agents.ollama_client import stream_ollama
            async for chunk in stream_ollama(
                base_url=base_url,
                model=model,
                messages=full_messages,
                temperature=temperature,
            ):
                yield chunk

    except Exception as exc:
        log.error("Agent %s failed: %s", agent.get("id"), exc)
        try:
            import httpx
            if isinstance(exc, httpx.ConnectError):
                yield "[Ollama is not running — start it with: python scripts/start_ollama.py]"
                return
        except ImportError:
            pass
        short = str(exc)[:120]
        yield f"[Error: {type(exc).__name__}: {short}]"
