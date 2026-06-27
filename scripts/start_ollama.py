"""
start_ollama.py — ensure the Ollama server and model are ready.

Usage:
    python scripts/start_ollama.py

Steps:
  1. Ping http://localhost:11434 — exit immediately if already up.
  2. Find the ollama executable (PATH, then common Windows install dirs).
  3. Launch "ollama serve" as a detached background process.
  4. Poll until the server responds (up to 30 s).
  5. Check whether the target model is already pulled; pull it if not.
  6. Print a ready message and exit 0.

If the executable is not found, print download instructions and exit 1.
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

OLLAMA_URL   = "http://localhost:11434"
MODEL        = "zephyr:7b-alpha-q4_K_M"
POLL_EVERY   = 1.0    # seconds between readiness checks
START_TIMEOUT = 30.0  # max seconds to wait for server to come up

# Common Windows install paths tried in order when not in PATH
_WIN_CANDIDATES = [
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Ollama", "ollama.exe"),
    r"C:\Program Files\Ollama\ollama.exe",
    os.path.join(os.environ.get("USERPROFILE", ""), "ollama", "ollama.exe"),
]


# ── helpers ────────────────────────────────────────────────────────────────────

def _get(path: str):
    """HTTP GET helper — returns parsed JSON or raises."""
    with urllib.request.urlopen(f"{OLLAMA_URL}{path}", timeout=5) as r:
        return json.loads(r.read())


def _ping() -> bool:
    try:
        _get("/api/tags")
        return True
    except Exception:
        return False


def _model_available() -> bool:
    try:
        data = _get("/api/tags")
        names = [m["name"] for m in data.get("models", [])]
        return MODEL in names
    except Exception:
        return False


def _find_executable() -> str | None:
    found = shutil.which("ollama")
    if found:
        return found
    for candidate in _WIN_CANDIDATES:
        if os.path.isfile(candidate):
            return candidate
    return None


def _launch_server(exe: str):
    """Start `ollama serve` detached so it keeps running after this script exits."""
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


def _pull_model(exe: str):
    """Pull the model — blocks until download is complete. Shows progress."""
    print(f">> Pulling model {MODEL} (this may take a while on first run)...")
    subprocess.run([exe, "pull", MODEL], check=True)


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    # 1. Already fully running?
    if _ping():
        print(f"[OK] Ollama server already running at {OLLAMA_URL}")
        if _model_available():
            print(f"[OK] Model {MODEL} is ready.")
            sys.exit(0)
        else:
            # Server is up but model not pulled yet
            exe = _find_executable()
            if exe:
                _pull_model(exe)
                print(f"[OK] Model {MODEL} pulled and ready.")
                sys.exit(0)
            else:
                print(f"[FAIL] Model {MODEL} is not pulled and ollama executable not found.")
                print(f"       Run manually:  ollama pull {MODEL}")
                sys.exit(1)

    # 2. Find the executable
    exe = _find_executable()
    if not exe:
        print("[FAIL] Ollama executable not found.\n")
        print("Download and install Ollama from:  https://ollama.com/download")
        print(f"Then pull your model:              ollama pull {MODEL}")
        sys.exit(1)

    # 3. Launch server
    print(f">> Starting Ollama server ({exe}) ...")
    _launch_server(exe)

    # 4. Wait for server to be ready
    deadline = time.monotonic() + START_TIMEOUT
    while time.monotonic() < deadline:
        if _ping():
            print(f"\n[OK] Ollama server is up at {OLLAMA_URL}")
            break
        print(".", end="", flush=True)
        time.sleep(POLL_EVERY)
    else:
        print(f"\n[FAIL] Server did not respond within {START_TIMEOUT:.0f} s.")
        print("       Try running `ollama serve` manually to see error output.")
        sys.exit(1)

    # 5. Ensure model is pulled
    if not _model_available():
        _pull_model(exe)

    print(f"[OK] Model {MODEL} is ready.")
    print(f"\nOllama is running. Start Round Table:  python src/main.py")
    sys.exit(0)


if __name__ == "__main__":
    main()
