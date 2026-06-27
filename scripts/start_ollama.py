"""
start_ollama.py — ensure Ollama is running before Round Table.

Usage:
    python scripts/start_ollama.py

Behaviour:
  1. Ping http://localhost:11434 — if already up, exit 0 immediately.
  2. Find the ollama executable (PATH &gt;&gt; common Windows install dirs).
  3. Launch `ollama serve` as a detached background process.
  4. Poll until the server responds (up to 30 s), then exit 0.
  5. If the executable is not found, print install instructions and exit 1.
"""
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

OLLAMA_URL  = "http://localhost:11434"
POLL_EVERY  = 1.0   # seconds between readiness checks
TIMEOUT     = 30.0  # max seconds to wait after launching

# Common Windows install paths (tried in order if not in PATH)
_WIN_CANDIDATES = [
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Ollama", "ollama.exe"),
    r"C:\Program Files\Ollama\ollama.exe",
    os.path.join(os.environ.get("USERPROFILE", ""), "ollama", "ollama.exe"),
]


def _ping() -> bool:
    """Return True if the Ollama API responds."""
    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3)
        return True
    except Exception:
        return False


def _find_executable() -> str | None:
    """Return path to the ollama binary, or None if not found."""
    found = shutil.which("ollama")
    if found:
        return found
    for candidate in _WIN_CANDIDATES:
        if os.path.isfile(candidate):
            return candidate
    return None


def _launch(exe: str):
    """Start `ollama serve` detached — it keeps running after this script exits."""
    if sys.platform == "win32":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        subprocess.Popen(
            [exe, "serve"],
            creationflags=flags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
    else:
        subprocess.Popen(
            [exe, "serve"],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def main():
    # ── Already running? ──────────────────────────────────────────────────────
    if _ping():
        print(f"[OK]  Ollama is already running at {OLLAMA_URL}")
        sys.exit(0)

    # ── Find the executable ───────────────────────────────────────────────────
    exe = _find_executable()
    if not exe:
        print("[FAIL]  Ollama executable not found.")
        print()
        print("Install Ollama from https://ollama.com/download")
        print("Then pull your model:  ollama pull zephyr:7b-alpha-q4_K_M")
        sys.exit(1)

    # ── Launch ────────────────────────────────────────────────────────────────
    print(f"&gt;&gt;  Starting Ollama ({exe}) ...")
    _launch(exe)

    # ── Wait for readiness ────────────────────────────────────────────────────
    deadline = time.monotonic() + TIMEOUT
    dots = 0
    while time.monotonic() < deadline:
        if _ping():
            print(f"\n[OK]  Ollama is ready at {OLLAMA_URL}")
            sys.exit(0)
        print(".", end="", flush=True)
        dots += 1
        time.sleep(POLL_EVERY)

    print(f"\n[FAIL]  Ollama did not respond within {TIMEOUT:.0f} s.")
    print("   Check logs with:  ollama serve")
    sys.exit(1)


if __name__ == "__main__":
    main()
