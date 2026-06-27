"""
Centralised logging for Prism.
Every module gets a child logger via get_logger(__name__).
All output goes to both the terminal and logs/app.log.
"""
import logging
import os
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"


def _setup() -> logging.Logger:
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(fmt)

    root = logging.getLogger("prism")
    root.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
    root.propagate = False

    root.info("─" * 60)
    root.info("Prism starting — log file: %s", LOG_FILE)
    return root


_root_logger = _setup()


def get_logger(name: str) -> logging.Logger:
    """Return a child logger namespaced under 'prism'."""
    # Strip 'src.' prefix if running from src/ directory
    clean = name.replace("src.", "") if name.startswith("src.") else name
    return _root_logger.getChild(clean)
