"""
Settings panel — slides in from the right as a Stack overlay.
Open:  offset=Offset(0, 0)
Closed: offset=Offset(1, 0)  (shifted off-screen to the right)
"""
import flet as ft
from ui.theme import (
    BG_PRIMARY, BG_SECONDARY, BORDER, TEXT_PRIMARY, TEXT_SECONDARY,
    AGENT_COLORS, CHAT_FONTS,
    FONT_SETTINGS_LABEL, FONT_SETTINGS_HEADER, FONT_SECTION_TITLE,
    SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG,
)

PANEL_WIDTH = 340
ANIM_MS = 280


def _label(text: str) -> ft.Text:
    return ft.Text(text, size=FONT_SETTINGS_LABEL, color=TEXT_SECONDARY, weight=ft.FontWeight.W_600)


def _section_header(text: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, size=FONT_SETTINGS_HEADER, weight=ft.FontWeight.W_700, color=TEXT_PRIMARY),
        padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=SPACE_MD, bottom=SPACE_SM),
    )


def _divider() -> ft.Divider:
    return ft.Divider(height=1, color=BORDER)


class _ColorSwatch(ft.Container):
    """Clickable color circle — shows checkmark when selected."""

    def __init__(self, color: str, selected: bool, on_pick):
        self._color = color
        self._on_pick = on_pick
        self._check = ft.Container(
            content=ft.Text("✓", size=14, color="#FFFFFF", weight=ft.FontWeight.W_700),
            alignment=ft.Alignment(0, 0),
            visible=selected,
        )
        super().__init__(
            content=self._check,
            width=32, height=32,
            bgcolor=color,
            border_radius=16,
            alignment=ft.Alignment(0, 0),
            border=ft.border.Border(
                top=ft.BorderSide(2, "#FFFFFF" if selected else color),
                bottom=ft.BorderSide(2, "#FFFFFF" if selected else color),
                left=ft.BorderSide(2, "#FFFFFF" if selected else color),
                right=ft.BorderSide(2, "#FFFFFF" if selected else color),
            ),
            on_click=self._click,
            animate_scale=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
        )

    def _click(self, e):
        self._on_pick(self._color)

    def set_selected(self, selected: bool):
        self._check.visible = selected
        self._check.update()


class _AgentTile(ft.ExpansionTile):
    def __init__(self, index: int, agent: dict, on_change):
        self._index = index
        self._agent = agent
        self._on_change = on_change
        self._swatches: list[_ColorSwatch] = []

        # Name field
        self._name_field = ft.TextField(
            value=agent["name"],
            label="Name",
            border_radius=8,
            border_color=BORDER,
            focused_border_color="#0084FF",
            text_size=13,
            on_change=lambda e: self._update("name", e.control.value),
        )

        # Persona field
        self._persona_field = ft.TextField(
            value=agent["persona"],
            label="Persona / rules",
            multiline=True,
            min_lines=2,
            max_lines=5,
            border_radius=8,
            border_color=BORDER,
            focused_border_color="#0084FF",
            text_size=13,
            on_change=lambda e: self._update("persona", e.control.value),
        )

        # Source dropdown
        self._source_dd = ft.Dropdown(
            value=agent["source"],
            label="Source",
            border_radius=8,
            border_color=BORDER,
            focused_border_color="#0084FF",
            options=[
                ft.DropdownOption(key="claude", text="Claude API"),
                ft.DropdownOption(key="ollama", text="Ollama (local)"),
            ],
            on_select=lambda e: self._update("source", e.control.value),
        )

        # Response length dropdown
        self._length_dd = ft.Dropdown(
            value=agent["response_length"],
            label="Response length",
            border_radius=8,
            border_color=BORDER,
            focused_border_color="#0084FF",
            options=[
                ft.DropdownOption(key="short", text="Short (1-2 sentences)"),
                ft.DropdownOption(key="medium", text="Medium (1 paragraph)"),
                ft.DropdownOption(key="long", text="Long (detailed)"),
            ],
            on_select=lambda e: self._update("response_length", e.control.value),
        )

        # Temperature slider
        self._temp_label = ft.Text(f"Temperature: {agent['temperature']:.1f}", size=FONT_SETTINGS_LABEL, color=TEXT_SECONDARY)
        self._temp_slider = ft.Slider(
            value=agent["temperature"],
            min=0.0, max=1.0, divisions=10,
            active_color="#0084FF",
            on_change=self._on_temp_change,
            expand=True,
        )

        # Color swatches
        swatch_row = self._build_swatch_row(agent["color"])

        # Enable switch
        self._enable_switch = ft.Switch(
            value=agent["enabled"],
            active_color="#0084FF",
            on_change=lambda e: self._update("enabled", e.control.value),
        )

        controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[_label("Active"), self._enable_switch],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        self._name_field,
                        _label("Color"),
                        swatch_row,
                        self._source_dd,
                        self._length_dd,
                        self._persona_field,
                        self._temp_label,
                        self._temp_slider,
                    ],
                    spacing=SPACE_SM,
                ),
                padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=SPACE_SM, bottom=SPACE_MD),
            )
        ]

        slot_num = index + 1
        super().__init__(
            title=ft.Text(agent["name"], size=13, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
            controls=controls,
            tile_padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=0, bottom=0),
            collapsed_bgcolor=BG_SECONDARY if not agent["enabled"] else BG_PRIMARY,
            bgcolor=BG_PRIMARY,
            text_color=TEXT_PRIMARY,
            icon_color=TEXT_SECONDARY,
        )

    def _build_swatch_row(self, selected_color: str) -> ft.Row:
        self._swatches = [
            _ColorSwatch(color, color == selected_color, self._on_color_pick)
            for color in AGENT_COLORS
        ]
        return ft.Row(controls=self._swatches, spacing=SPACE_SM)

    def _on_color_pick(self, color: str):
        self._update("color", color)
        for sw in self._swatches:
            sw.set_selected(sw._color == color)
            sw.update()

    def _on_temp_change(self, e):
        val = round(e.control.value, 1)
        self._temp_label.value = f"Temperature: {val:.1f}"
        self._temp_label.update()
        self._update("temperature", val)

    def _update(self, key: str, value):
        self._agent[key] = value
        if key == "name":
            self.title = ft.Text(value or f"Agent {self._index + 1}", size=13, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY)
            self.update()
        self._on_change(self._index, self._agent)

    def refresh_name(self):
        self.title = ft.Text(self._agent["name"], size=13, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY)
        self.update()


class SettingsPanel(ft.Container):
    def __init__(self, on_close, on_save, on_appearance_change):
        self._on_close = on_close
        self._on_save = on_save
        self._on_appearance_change = on_appearance_change

        from data.settings_store import SettingsStore
        self._store = SettingsStore.instance()

        self._visible_flag = False

        # ── Appearance section ────────────────────────────────────────────────
        app = self._store.appearance
        self._font_size_label = ft.Text(
            f"Font size: {app['font_size']}px",
            size=FONT_SETTINGS_LABEL, color=TEXT_SECONDARY,
        )
        self._font_size_slider = ft.Slider(
            value=float(app["font_size"]),
            min=11, max=22, divisions=11,
            active_color="#0084FF",
            on_change=self._on_font_size_change,
            expand=True,
        )
        self._font_dd = ft.Dropdown(
            value=app["font_family"],
            label="Font family",
            border_radius=8,
            border_color=BORDER,
            focused_border_color="#0084FF",
            options=[ft.DropdownOption(key=f, text=f) for f in CHAT_FONTS],
            on_select=self._on_font_change,
            expand=True,
        )
        self._zoom_label = ft.Text(
            f"Zoom: {int(app['zoom'] * 100)}%",
            size=FONT_SETTINGS_LABEL, color=TEXT_SECONDARY,
        )
        self._zoom_slider = ft.Slider(
            value=app["zoom"] * 100,
            min=75, max=150, divisions=15,
            active_color="#0084FF",
            on_change=self._on_zoom_change,
            expand=True,
        )

        appearance_section = ft.Column(
            controls=[
                _section_header("💬 Chat Appearance"),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self._font_size_label,
                            self._font_size_slider,
                            self._zoom_label,
                            self._zoom_slider,
                            self._font_dd,
                        ],
                        spacing=SPACE_XS,
                    ),
                    padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=0, bottom=SPACE_MD),
                ),
                _divider(),
            ],
            spacing=0,
        )

        # ── Global section ────────────────────────────────────────────────────
        glb = self._store.global_cfg
        self._api_key_field = ft.TextField(
            value=glb["claude_api_key"],
            label="Claude API key",
            password=True,
            can_reveal_password=True,
            border_radius=8,
            border_color=BORDER,
            focused_border_color="#0084FF",
            text_size=13,
            on_change=lambda e: self._store.global_cfg.update({"claude_api_key": e.control.value}),
        )
        self._ollama_field = ft.TextField(
            value=glb["ollama_url"],
            label="Ollama URL",
            border_radius=8,
            border_color=BORDER,
            focused_border_color="#0084FF",
            text_size=13,
            on_change=lambda e: self._store.global_cfg.update({"ollama_url": e.control.value}),
        )
        self._agent_delay_label = ft.Text(
            f"Between agents: {glb['inter_agent_delay']:.1f}s",
            size=FONT_SETTINGS_LABEL, color=TEXT_SECONDARY,
        )
        self._agent_delay_slider = ft.Slider(
            value=glb["inter_agent_delay"],
            min=0.5, max=8.0, divisions=15,
            active_color="#0084FF",
            on_change=self._on_agent_delay_change,
            expand=True,
        )
        self._round_delay_label = ft.Text(
            f"Between rounds: {glb['inter_round_delay']:.1f}s",
            size=FONT_SETTINGS_LABEL, color=TEXT_SECONDARY,
        )
        self._round_delay_slider = ft.Slider(
            value=glb["inter_round_delay"],
            min=1.0, max=15.0, divisions=14,
            active_color="#0084FF",
            on_change=self._on_round_delay_change,
            expand=True,
        )

        global_section = ft.Column(
            controls=[
                _section_header("🌐 Global"),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self._api_key_field,
                            self._ollama_field,
                            self._agent_delay_label,
                            self._agent_delay_slider,
                            self._round_delay_label,
                            self._round_delay_slider,
                        ],
                        spacing=SPACE_SM,
                    ),
                    padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=0, bottom=SPACE_MD),
                ),
                _divider(),
            ],
            spacing=0,
        )

        # ── Agent tiles ───────────────────────────────────────────────────────
        self._agent_tiles = [
            _AgentTile(i, self._store.agents[i], self._on_agent_change)
            for i in range(5)
        ]

        agents_section = ft.Column(
            controls=[
                _section_header("🤖 Agents"),
                *self._agent_tiles,
            ],
            spacing=0,
        )

        # ── Save button ───────────────────────────────────────────────────────
        save_btn = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Text("Save", color="#FFFFFF", size=14, weight=ft.FontWeight.W_600),
                bgcolor="#0084FF",
                elevation=0,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding(left=0, right=0, top=14, bottom=14),
                    overlay_color="#FFFFFF26",
                ),
                expand=True,
                on_click=self._handle_save,
            ),
            padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=SPACE_MD, bottom=SPACE_LG),
        )

        # ── Header ────────────────────────────────────────────────────────────
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("Settings", size=FONT_SECTION_TITLE, weight=ft.FontWeight.W_700, color=TEXT_PRIMARY),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=TEXT_SECONDARY,
                        icon_size=20,
                        on_click=lambda e: self._on_close(),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=SPACE_MD, right=SPACE_SM, top=0, bottom=0),
            height=48,
            border=ft.border.Border(bottom=ft.BorderSide(1, BORDER)),
        )

        scrollable = ft.Column(
            controls=[
                appearance_section,
                global_section,
                agents_section,
                save_btn,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            expand=True,
        )

        super().__init__(
            content=ft.Column(
                controls=[header, scrollable],
                spacing=0,
                expand=True,
            ),
            width=PANEL_WIDTH,
            top=0,
            bottom=0,
            right=0,
            bgcolor=BG_PRIMARY,
            border=ft.border.Border(left=ft.BorderSide(1, BORDER)),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=24, color="#00000022", offset=ft.Offset(-4, 0)),
            animate_offset=ft.Animation(ANIM_MS, ft.AnimationCurve.EASE_OUT),
            offset=ft.Offset(1, 0),
            visible=False,
        )

    # ── Open / close ──────────────────────────────────────────────────────────

    def open(self):
        self.visible = True
        self.offset = ft.Offset(0, 0)
        self.update()

    def close(self):
        self.offset = ft.Offset(1, 0)
        self.update()
        import asyncio
        if self.page:
            self.page.run_task(self._hide_after_anim)

    async def _hide_after_anim(self):
        import asyncio
        await asyncio.sleep(ANIM_MS / 1000 + 0.05)
        self.visible = False
        self.update()

    # ── Appearance handlers ───────────────────────────────────────────────────

    def _on_font_size_change(self, e):
        val = int(e.control.value)
        self._font_size_label.value = f"Font size: {val}px"
        self._font_size_label.update()
        self._store.appearance["font_size"] = val
        self._on_appearance_change(self._store.appearance)

    def _on_font_change(self, e):
        self._store.appearance["font_family"] = e.control.value
        self._on_appearance_change(self._store.appearance)

    def _on_zoom_change(self, e):
        pct = int(e.control.value)
        self._zoom_label.value = f"Zoom: {pct}%"
        self._zoom_label.update()
        self._store.appearance["zoom"] = pct / 100
        self._on_appearance_change(self._store.appearance)

    # ── Global handlers ───────────────────────────────────────────────────────

    def _on_agent_delay_change(self, e):
        val = round(e.control.value, 1)
        self._agent_delay_label.value = f"Between agents: {val:.1f}s"
        self._agent_delay_label.update()
        self._store.global_cfg["inter_agent_delay"] = val

    def _on_round_delay_change(self, e):
        val = round(e.control.value, 1)
        self._round_delay_label.value = f"Between rounds: {val:.1f}s"
        self._round_delay_label.update()
        self._store.global_cfg["inter_round_delay"] = val

    # ── Agent handler ─────────────────────────────────────────────────────────

    def _on_agent_change(self, index: int, agent: dict):
        self._store.agents[index].update(agent)

    # ── Save ──────────────────────────────────────────────────────────────────

    def _handle_save(self, e):
        self._store.save()
        self._on_save(self._store)
        self._on_close()
