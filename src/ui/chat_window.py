"""
Main layout: assembles TitleBar + ControlBar + ChatArea + InputBar.
Phase 1: wired to demo messages only — no real AI calls.
"""
import asyncio
import traceback
import flet as ft

from utils.logger import get_logger
from ui.theme import BG_PRIMARY, AGENT_COLORS

log = get_logger(__name__)
from ui.title_bar import TitleBar
from ui.control_bar import ControlBar
from ui.chat_area import ChatArea
from ui.bubble import AgentBubble, UserBubble, SystemMessage
from ui.typing_indicator import TypingIndicator
from ui.input_bar import InputBar

# ── Demo data ─────────────────────────────────────────────────────────────────
DEMO_AGENTS = [
    {"id": "agent_1", "name": "Devil's Advocate 😈", "color": AGENT_COLORS[3]},  # dark red
    {"id": "agent_2", "name": "Optimist 🌟",          "color": AGENT_COLORS[0]},  # green
    {"id": "agent_3", "name": "Realist 🔍",           "color": AGENT_COLORS[1]},  # violet
]

DEMO_MESSAGES = [
    {"type": "system",  "text": "Session started · 3 agents active"},
    {"type": "user",    "content": "Let's brainstorm a subscription model for the app. What do you all think?"},
    {"type": "agent",   "agent": DEMO_AGENTS[0], "content": "The subscription model has a critical flaw nobody has addressed: customer acquisition cost. If CAC exceeds $27 you can't break even in Q1 at $9/month. 😤"},
    {"type": "agent",   "agent": DEMO_AGENTS[1], "content": "I love this direction! 🚀 The market timing is perfect — subscription fatigue is reversing as people consolidate services. The trend is our friend here."},
    {"type": "agent",   "agent": DEMO_AGENTS[2], "content": "Both valid points. The real question is whether we're B2B or B2C. Those are completely different unit economics and neither of you has defined that yet."},
    {"type": "user",    "content": "Good point. Let's say B2B — teams of 5–20 people."},
    {"type": "agent",   "agent": DEMO_AGENTS[0], "content": "B2B changes everything. CAC through sales channels is 3–8x higher but LTV scales with seats. At $25/seat/month a 10-person team is $3k ARR. That's workable. 🤔"},
    {"type": "agent",   "agent": DEMO_AGENTS[1], "content": "Exactly! And teams renew at 85–90% vs 60% for consumers. This is the right call. We should also consider a free tier for solo users to drive bottom-up adoption 🎯"},
]


class ChatWindow(ft.Column):
    """Root UI component — full window layout."""

    def __init__(self):
        self._thoughts_on = True
        self._autonomous_running = False
        self._demo_loaded = False

        self._chat = ChatArea()
        self._input = InputBar(on_send=self._handle_user_send)
        self._control = ControlBar(on_start=self._handle_start, on_stop=self._handle_stop)
        self._title = TitleBar(
            on_settings=self._handle_settings,
            on_toggle_thoughts=self._handle_toggle_thoughts,
            thoughts_on=self._thoughts_on,
        )

        super().__init__(
            controls=[self._title, self._control, self._chat, self._input],
            expand=True,
            spacing=0,
        )

    def did_mount(self):
        self.page.run_task(self._load_demo)

    # ── Demo loader ───────────────────────────────────────────────────────────

    async def _load_demo(self):
        """Replay demo messages with pacing to show the UI in action."""
        log.info("Loading demo conversation")
        try:
            await asyncio.sleep(0.3)
        except Exception:
            log.error("_load_demo failed:\n%s", traceback.format_exc())
            return
        prev_sender = None

        for msg in DEMO_MESSAGES:
            if msg["type"] == "system":
                self._chat.add(SystemMessage(msg["text"]))
                await asyncio.sleep(0.3)

            elif msg["type"] == "user":
                self._chat.add(UserBubble(content=msg["content"]))
                prev_sender = "user"
                await asyncio.sleep(0.8)

            elif msg["type"] == "agent":
                agent = msg["agent"]
                show_name = prev_sender != agent["id"]

                # Show typing indicator
                indicator = TypingIndicator(agent["name"], agent["color"])
                self._chat.add(indicator)
                await asyncio.sleep(1.5)

                # Swap for real bubble
                self._chat.remove(indicator)
                bubble = AgentBubble(
                    content=msg["content"],
                    agent_name=agent["name"],
                    agent_color=agent["color"],
                    show_name=show_name,
                )
                self._chat.add(bubble)
                prev_sender = agent["id"]
                await asyncio.sleep(0.8)

        self._demo_loaded = True

    # ── User input ────────────────────────────────────────────────────────────

    def _handle_user_send(self, text: str):
        self._chat.add(UserBubble(content=text))
        # Phase 1: just echo — no AI call yet
        # Phase 3 will wire up the real agent runner here

    # ── Autonomous mode ───────────────────────────────────────────────────────

    def _handle_start(self):
        self._autonomous_running = True
        self._control.set_running(round_num=1)
        self._input.set_disabled(False)
        # Phase 7 will wire the real autonomous loop here
        self._chat.add(SystemMessage("Autonomous mode started — agents are thinking..."))

    def _handle_stop(self):
        self._autonomous_running = False
        self._control.set_stopping()
        # Immediately go idle in Phase 1 (no active generation to wait for)
        self._control.set_idle()
        self._chat.add(SystemMessage("Autonomous mode stopped."))

    # ── Settings ──────────────────────────────────────────────────────────────

    def _handle_settings(self):
        # Phase 2 will render the settings panel here
        self._chat.add(SystemMessage("⚙ Settings panel — coming in Phase 2"))

    def _handle_toggle_thoughts(self, enabled: bool):
        self._thoughts_on = enabled
        state = "ON" if enabled else "OFF"
        self._chat.add(SystemMessage(f"💭 Thoughts panel {state}"))
