"""
Persistent settings storage. Atomic JSON writes — write to .tmp then rename.
All callers get a reference to the singleton via SettingsStore.instance().
"""
import json
import os
import shutil

from ui.theme import (
    AGENT_COLORS, CHAT_FONT_DEFAULT, CHAT_FONT_SIZE_DEFAULT, CHAT_ZOOM_DEFAULT,
)
from utils.logger import get_logger

log = get_logger(__name__)

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
_SETTINGS_PATH = os.path.join(_DATA_DIR, "settings.json")

_DEFAULT_AGENTS = [
    {"id": f"agent_{i+1}", "enabled": i < 3, "name": f"Agent {i+1}",
     "color": AGENT_COLORS[i], "source": "ollama", "persona": "",
     "response_length": "medium", "temperature": 0.7}
    for i in range(5)
]


def default_agent(index: int) -> dict:
    """Return a fresh default config for the given agent slot (0-based)."""
    import copy
    return copy.deepcopy(_DEFAULT_AGENTS[index])


def default_settings() -> dict:
    """Return a fresh copy of all defaults (appearance + global + agents)."""
    import copy
    return copy.deepcopy(_DEFAULTS)

_DEFAULTS = {
    "appearance": {
        "font_size": CHAT_FONT_SIZE_DEFAULT,
        "font_family": CHAT_FONT_DEFAULT,
        "zoom": CHAT_ZOOM_DEFAULT,
    },
    "global": {
        "claude_api_key": "",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "zephyr:7b-alpha-q4_K_M",
        "inter_agent_delay": 2.0,
        "inter_round_delay": 4.0,
    },
    "agents": _DEFAULT_AGENTS,
}


class SettingsStore:
    _instance: "SettingsStore | None" = None

    def __init__(self):
        self._data: dict = {}
        self._load()

    @classmethod
    def instance(cls) -> "SettingsStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── Public accessors ──────────────────────────────────────────────────────

    @property
    def appearance(self) -> dict:
        return self._data["appearance"]

    @property
    def global_cfg(self) -> dict:
        return self._data["global"]

    @property
    def agents(self) -> list:
        return self._data["agents"]

    def agent(self, index: int) -> dict:
        return self._data["agents"][index]

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self):
        os.makedirs(_DATA_DIR, exist_ok=True)
        tmp = _SETTINGS_PATH + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
            shutil.move(tmp, _SETTINGS_PATH)
            log.debug("Settings saved to %s", _SETTINGS_PATH)
        except Exception as exc:
            log.error("Failed to save settings: %s", exc)
            if os.path.exists(tmp):
                os.remove(tmp)

    def _load(self):
        import copy
        self._data = copy.deepcopy(_DEFAULTS)
        if not os.path.exists(_SETTINGS_PATH):
            return
        try:
            with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            self._deep_merge(self._data, saved)
            log.debug("Settings loaded from %s", _SETTINGS_PATH)
        except Exception as exc:
            log.warning("Could not load settings (%s) — using defaults", exc)

    @staticmethod
    def _deep_merge(base: dict, override: dict):
        for key, val in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(val, dict):
                SettingsStore._deep_merge(base[key], val)
            else:
                base[key] = val
