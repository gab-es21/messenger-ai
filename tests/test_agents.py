"""
Tests for Phase 3 agent logic — no real API calls.
Clients are stubbed; runner and history are tested with fake streams.
"""
import sys, os, asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# ── history.py ────────────────────────────────────────────────────────────────

def test_history_user_message():
    from agents.history import build_messages
    log = [{"type": "user", "content": "Hello"}]
    msgs = build_messages(log, "agent_1")
    assert msgs == [{"role": "user", "content": "Hello"}]


def test_history_own_reply_is_assistant():
    from agents.history import build_messages
    log = [
        {"type": "user", "content": "Hi"},
        {"type": "agent", "agent_id": "agent_1", "agent_name": "A1", "content": "Hey"},
    ]
    msgs = build_messages(log, "agent_1")
    assert msgs[-1] == {"role": "assistant", "content": "Hey"}


def test_history_other_agent_prefixed():
    from agents.history import build_messages
    log = [
        {"type": "user", "content": "Hi"},
        {"type": "agent", "agent_id": "agent_2", "agent_name": "Optimist", "content": "Great!"},
    ]
    msgs = build_messages(log, "agent_1")
    assert msgs[-1]["role"] == "user"
    assert "[Optimist]:" in msgs[-1]["content"]


def test_history_system_entries_skipped():
    from agents.history import build_messages
    log = [
        {"type": "system", "text": "Session started"},
        {"type": "user", "content": "Go"},
    ]
    msgs = build_messages(log, "agent_1")
    assert len(msgs) == 1
    assert msgs[0]["role"] == "user"


def test_history_max_trimmed():
    from agents.history import build_messages, MAX_HISTORY
    log = [{"type": "user", "content": f"msg {i}"} for i in range(MAX_HISTORY + 10)]
    msgs = build_messages(log, "agent_1")
    assert len(msgs) == MAX_HISTORY


# ── runner.py — no API calls ─────────────────────────────────────────────────

def _collect(agen):
    """Run an async generator synchronously and collect output."""
    loop = asyncio.new_event_loop()
    chunks = []
    async def _run():
        async for c in agen:
            chunks.append(c)
    loop.run_until_complete(_run())
    loop.close()
    return chunks


def test_runner_no_messages_yields_nothing():
    from agents.runner import run_agent_turn
    agent = {"id": "agent_1", "name": "A", "source": "ollama",
             "persona": "", "response_length": "medium", "temperature": 0.7}
    chunks = _collect(run_agent_turn(agent, [], {}))
    assert chunks == []


def test_runner_claude_missing_key_yields_error():
    from agents.runner import run_agent_turn
    agent = {"id": "agent_1", "name": "A", "source": "claude",
             "persona": "", "response_length": "medium", "temperature": 0.7}
    log = [{"type": "user", "content": "hi"}]
    chunks = _collect(run_agent_turn(agent, log, {"claude_api_key": ""}))
    assert len(chunks) == 1
    assert "Error" in chunks[0]
    assert "API key" in chunks[0]


def test_runner_ollama_connection_error_yields_error():
    from agents.runner import run_agent_turn
    agent = {"id": "agent_1", "name": "A", "source": "ollama",
             "persona": "", "response_length": "short", "temperature": 0.5}
    log = [{"type": "user", "content": "hi"}]
    # Port 1 is always refused
    cfg = {"ollama_url": "http://localhost:1", "ollama_model": "fake"}
    chunks = _collect(run_agent_turn(agent, log, cfg))
    assert len(chunks) == 1
    assert "Error" in chunks[0]
