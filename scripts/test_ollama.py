"""
test_ollama.py — smoke-test the local Ollama model.

Usage:
    python scripts/test_ollama.py

Sends a simple non-streaming request and prints the model's reply.
Run this after start_ollama.py to confirm everything works end-to-end.
"""
import json
import sys
import urllib.error
import urllib.request

URL   = "http://localhost:11434/api/chat"
MODEL = "zephyr:7b-alpha-q4_K_M"

PAYLOAD = {
    "model": MODEL,
    "stream": False,
    "messages": [
        {
            "role": "system",
            "content": (
                "You are a sharp, direct participant in a brainstorming session. "
                "Keep replies to 1-2 sentences."
            ),
        },
        {
            "role": "user",
            "content": "What is the single biggest risk of launching a SaaS product too early?",
        },
    ],
}


def main():
    print(f"Testing Ollama at {URL}")
    print(f"Model: {MODEL}\n")

    data = json.dumps(PAYLOAD).encode()
    req  = urllib.request.Request(
        URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = json.loads(resp.read())
    except urllib.error.URLError as exc:
        print(f"[FAIL] Could not reach Ollama: {exc}")
        print("       Make sure Ollama is running:  python scripts/start_ollama.py")
        sys.exit(1)

    reply = result.get("message", {}).get("content", "").strip()
    if not reply:
        print("[FAIL] Empty reply — check the model name and server logs.")
        sys.exit(1)

    print(f"Model reply:\n\n  {reply}\n")
    print("[OK] Ollama is working correctly.")


if __name__ == "__main__":
    main()
