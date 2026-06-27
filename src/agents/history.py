"""Convert the ChatWindow message log into API-ready messages for one agent."""

MAX_HISTORY = 40  # older messages are dropped to keep context reasonable


def build_messages(log: list[dict], this_agent_id: str) -> list[dict]:
    """
    Map Round Table message log → OpenAI-style role/content list.

    - user entries          → role=user
    - this agent's entries  → role=assistant
    - other agents' entries → role=user, prefixed with [Name]:
    - system entries        → skipped (UI metadata only)

    The last MAX_HISTORY entries are used; older ones are silently dropped.
    """
    out: list[dict] = []
    for entry in log[-MAX_HISTORY:]:
        t = entry.get("type")
        if t == "user":
            out.append({"role": "user", "content": entry["content"]})
        elif t == "agent":
            if entry.get("agent_id") == this_agent_id:
                out.append({"role": "assistant", "content": entry["content"]})
            else:
                name = entry.get("agent_name", "Agent")
                out.append({"role": "user", "content": f"[{name}]: {entry['content']}"})
    return out
