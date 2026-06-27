"""
Main layout: Stack containing the full-window Column + settings overlay.
Stores all messages so the chat can be rebuilt when font size/zoom changes.
"""
import asyncio
import copy
import traceback
import flet as ft

from utils.logger import get_logger
from ui.theme import BG_PRIMARY, AGENT_COLORS, CHAT_FONT_SIZE_DEFAULT, CHAT_ZOOM_DEFAULT
from ui.title_bar import TitleBar
from ui.control_bar import ControlBar
from ui.chat_area import ChatArea
from ui.bubble import AgentBubble, UserBubble, SystemMessage
from ui.typing_indicator import TypingIndicator
from ui.input_bar import InputBar
from ui.settings_panel import SettingsPanel

log = get_logger(__name__)

# ── Demo data ─────────────────────────────────────────────────────────────────
DEMO_AGENTS = [
    {"id": "agent_1", "name": "Devil's Advocate 😈", "color": AGENT_COLORS[3]},
    {"id": "agent_2", "name": "Optimist 🌟",          "color": AGENT_COLORS[0]},
    {"id": "agent_3", "name": "Realist 🔍",           "color": AGENT_COLORS[1]},
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


class ChatWindow(ft.Stack):
    """Root UI component — full window layout with settings overlay."""

    def __init__(self):
        self._thoughts_on = True
        self._autonomous_running = False
        self._demo_loaded = False
        self._message_log: list[dict] = []   # stored for font-size rebuild

        self._chat = ChatArea()
        self._input = InputBar(on_send=self._handle_user_send)
        self._control = ControlBar(on_start=self._handle_start, on_stop=self._handle_stop)
        self._title = TitleBar(
            on_settings=self._open_settings,
            on_toggle_thoughts=self._handle_toggle_thoughts,
            on_clear_chat=self._handle_clear_chat,
            thoughts_on=self._thoughts_on,
        )

        self._main = ft.Column(
            controls=[self._title, self._control, self._chat, self._input],
            expand=True,
            spacing=0,
        )

        self._settings_panel = SettingsPanel(
            on_close=self._close_settings,
            on_save=self._handle_settings_save,
            on_appearance_change=self._apply_appearance,
            on_appearance_revert=self._revert_appearance,
        )

        super().__init__(
            controls=[self._main, self._settings_panel],
            expand=True,
        )

    def did_mount(self):
        self.page.run_task(self._load_demo)

    # ── Effective font size ───────────────────────────────────────────────────

    def _effective_font_size(self) -> int:
        from data.settings_store import SettingsStore
        app = SettingsStore.instance().appearance
        base = app.get("font_size", CHAT_FONT_SIZE_DEFAULT)
        zoom = app.get("zoom", CHAT_ZOOM_DEFAULT)
        return max(9, min(28, int(base * zoom)))

    # ── Message helpers ───────────────────────────────────────────────────────

    def _add_user(self, content: str, animate: bool = True):
        entry = {"type": "user", "content": content}
        self._message_log.append(entry)
        b = UserBubble(content=content, font_size=self._effective_font_size())
        if not animate:
            b._bubble.opacity = 1
            b._bubble.offset = ft.Offset(0, 0)
        self._chat.add(b)

    def _add_agent(self, content: str, agent_name: str, agent_color: str,
                   show_name: bool = True, animate: bool = True):
        entry = {"type": "agent", "content": content,
                 "agent_name": agent_name, "agent_color": agent_color,
                 "show_name": show_name}
        self._message_log.append(entry)
        b = AgentBubble(
            content=content, agent_name=agent_name, agent_color=agent_color,
            show_name=show_name, font_size=self._effective_font_size(),
        )
        if not animate:
            b._bubble.opacity = 1
            b._bubble.offset = ft.Offset(0, 0)
        self._chat.add(b)

    def _add_system(self, text: str):
        entry = {"type": "system", "text": text}
        self._message_log.append(entry)
        self._chat.add(SystemMessage(text))

    def _rebuild_chat(self):
        """Clear and re-add all stored messages with current font size."""
        self._chat.clear()
        fz = self._effective_font_size()
        for entry in self._message_log:
            if entry["type"] == "user":
                b = UserBubble(content=entry["content"], font_size=fz)
                b._bubble.opacity = 1
                b._bubble.offset = ft.Offset(0, 0)
                self._chat.add(b)
            elif entry["type"] == "agent":
                b = AgentBubble(
                    content=entry["content"],
                    agent_name=entry["agent_name"],
                    agent_color=entry["agent_color"],
                    show_name=entry["show_name"],
                    font_size=fz,
                )
                b._bubble.opacity = 1
                b._bubble.offset = ft.Offset(0, 0)
                self._chat.add(b)
            elif entry["type"] == "system":
                self._chat.add(SystemMessage(entry["text"]))

    # ── Demo loader ───────────────────────────────────────────────────────────

    async def _load_demo(self):
        log.info("Loading demo conversation")
        try:
            await asyncio.sleep(0.3)
        except Exception:
            log.error("_load_demo failed:\n%s", traceback.format_exc())
            return
        prev_sender = None

        for msg in DEMO_MESSAGES:
            if msg["type"] == "system":
                self._add_system(msg["text"])
                await asyncio.sleep(0.3)

            elif msg["type"] == "user":
                self._add_user(msg["content"])
                prev_sender = "user"
                await asyncio.sleep(0.8)

            elif msg["type"] == "agent":
                agent = msg["agent"]
                show_name = prev_sender != agent["id"]

                indicator = TypingIndicator(agent["name"], agent["color"])
                self._chat.add(indicator)
                await asyncio.sleep(1.5)

                self._chat.remove(indicator)
                self._add_agent(
                    content=msg["content"],
                    agent_name=agent["name"],
                    agent_color=agent["color"],
                    show_name=show_name,
                )
                prev_sender = agent["id"]
                await asyncio.sleep(0.8)

        self._demo_loaded = True

    # ── User input ────────────────────────────────────────────────────────────

    def _handle_user_send(self, text: str):
        self._add_user(text)

    # ── Autonomous mode ───────────────────────────────────────────────────────

    def _handle_start(self):
        self._autonomous_running = True
        self._control.set_running(round_num=1)
        self._add_system("Autonomous mode started — agents are thinking...")

    def _handle_stop(self):
        self._autonomous_running = False
        self._control.set_stopping()
        self._control.set_idle()
        self._add_system("Autonomous mode stopped.")

    # ── Settings ──────────────────────────────────────────────────────────────

    def _open_settings(self):
        self._settings_panel.open()

    def _close_settings(self):
        self._settings_panel.close()

    def _handle_settings_save(self, store):
        log.info("Settings saved")
        self._rebuild_chat()

    def _apply_appearance(self, appearance: dict):
        """Live-apply font/zoom — rebuilds chat so text reflows naturally."""
        if self.page:
            font = appearance.get("font_family", "Roboto")
            self.page.theme = ft.Theme(font_family=font)
            self.page.update()
        self._rebuild_chat()

    def _revert_appearance(self, original_appearance: dict):
        """Called on Cancel — restores original appearance."""
        from data.settings_store import SettingsStore
        SettingsStore.instance().appearance.update(original_appearance)
        self._apply_appearance(original_appearance)

    def _handle_clear_chat(self):
        """Clear chat messages. Agent memories (data/agents/) are NOT touched."""
        self._message_log.clear()
        self._chat.clear()
        self._chat.add(SystemMessage("Chat cleared — agent memories are preserved."))
        self._message_log.append({"type": "system", "text": "Chat cleared — agent memories are preserved."})

    # ── Thoughts toggle ───────────────────────────────────────────────────────

    def _handle_toggle_thoughts(self, enabled: bool):
        self._thoughts_on = enabled
        state = "ON" if enabled else "OFF"
        self._add_system(f"💭 Thoughts panel {state}")
