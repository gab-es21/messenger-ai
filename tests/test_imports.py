"""
Module import tests — catches syntax errors and missing dependencies early.
Run with: python -m pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_import_theme():
    from ui.theme import (
        BG_PRIMARY, BG_SECONDARY, USER_BUBBLE, AGENT_COLORS,
        TITLE_BAR_HEIGHT, CONTROL_BAR_HEIGHT, INPUT_BAR_HEIGHT,
        BUBBLE_RADIUS, BUBBLE_MAX_WIDTH, DOT_SIZE, DOT_DELAYS,
    )
    assert len(AGENT_COLORS) == 12
    assert len(DOT_DELAYS) == 3


def test_import_bubble():
    from ui.bubble import UserBubble, AgentBubble, SystemMessage


def test_import_typing_indicator():
    from ui.typing_indicator import TypingIndicator


def test_import_input_bar():
    from ui.input_bar import InputBar


def test_import_chat_area():
    from ui.chat_area import ChatArea


def test_import_control_bar():
    from ui.control_bar import ControlBar


def test_import_title_bar():
    from ui.title_bar import TitleBar


def test_import_chat_window():
    from ui.chat_window import ChatWindow


def test_import_agent_dataclass():
    from agents.agent import AgentProfile
    a = AgentProfile(id="agent_1", name="Test", color="#FF0000")
    assert a.source == "claude"
    assert a.response_length == "medium"


def test_import_logger():
    from utils.logger import get_logger
    log = get_logger("test")
    assert log is not None
