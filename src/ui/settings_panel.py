"""
Settings panel — slides in from the right as a Stack overlay.

UX rules:
- Changes are held in a _draft dict; store is NOT mutated until Save.
- Appearance changes (font/zoom) fire on_appearance_change for live preview.
- Cancel restores original values via on_appearance_revert, then discards draft.
- Save commits draft to store and persists to disk.
- A sticky grey footer with Save / Cancel appears as soon as any value changes.
"""
import copy
import flet as ft
from ui.theme import (
    BG_PRIMARY, BG_SECONDARY, BORDER, TEXT_PRIMARY, TEXT_SECONDARY,
    AGENT_COLORS, CHAT_FONTS,
    FONT_SETTINGS_LABEL, FONT_SETTINGS_HEADER, FONT_SECTION_TITLE,
    SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG,
)

PANEL_WIDTH = 340
ANIM_MS = 280
FOOTER_BG = "#F2F3F5"


def _label(text: str) -> ft.Text:
    return ft.Text(text, size=FONT_SETTINGS_LABEL, color=TEXT_SECONDARY, weight=ft.FontWeight.W_600)


def _section_header(text: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, size=FONT_SETTINGS_HEADER, weight=ft.FontWeight.W_700, color=TEXT_PRIMARY),
        padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=SPACE_MD, bottom=SPACE_SM),
    )


def _divider() -> ft.Divider:
    return ft.Divider(height=1, color=BORDER)


class _ColorSwatch(ft.Stack):
    """Color circle. Shows a checkmark when selected; a red slash when taken by another agent."""

    def __init__(self, color: str, selected: bool, taken: bool, on_pick):
        self._color = color
        self._on_pick = on_pick
        self._taken = taken
        self._selected = selected

        self._circle = ft.Container(
            width=28, height=28,
            bgcolor=color,
            border_radius=14,
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                "✓", size=11, color="#FFFFFF",
                weight=ft.FontWeight.W_700,
                visible=selected and not taken,
            ),
            border=ft.border.Border(
                top=ft.BorderSide(2, "#FFFFFF" if (selected and not taken) else color),
                bottom=ft.BorderSide(2, "#FFFFFF" if (selected and not taken) else color),
                left=ft.BorderSide(2, "#FFFFFF" if (selected and not taken) else color),
                right=ft.BorderSide(2, "#FFFFFF" if (selected and not taken) else color),
            ),
            opacity=0.4 if taken else 1.0,
            on_click=self._click,
        )
        self._slash = ft.Container(
            content=ft.Text("/", size=30, color="#EE1111", weight=ft.FontWeight.W_900),
            alignment=ft.Alignment(0, -0.1),
            width=28, height=28,
            visible=taken,
        )
        super().__init__(controls=[self._circle, self._slash], width=28, height=28)

    def _click(self, e):
        if not self._taken:
            self._on_pick(self._color)

    def set_state(self, selected: bool, taken: bool):
        self._selected = selected
        self._taken = taken
        sel_ring = selected and not taken
        self._circle.content.visible = sel_ring
        self._circle.border = ft.border.Border(
            top=ft.BorderSide(2, "#FFFFFF" if sel_ring else self._color),
            bottom=ft.BorderSide(2, "#FFFFFF" if sel_ring else self._color),
            left=ft.BorderSide(2, "#FFFFFF" if sel_ring else self._color),
            right=ft.BorderSide(2, "#FFFFFF" if sel_ring else self._color),
        )
        self._circle.opacity = 0.4 if taken else 1.0
        self._circle.on_click = self._click  # still clickable only when not taken
        self._slash.visible = taken
        if self.page:
            self.update()


class _AgentTile(ft.ExpansionTile):
    """Collapsible agent config. Header shows color dot + enabled badge."""

    def __init__(self, index: int, draft_agent: dict, all_draft_agents: list,
                 on_change, on_color_pick=None):
        self._index = index
        self._d = draft_agent          # points into parent's draft dict
        self._on_change = on_change
        self._on_color_pick_cb = on_color_pick
        self._swatches: list[_ColorSwatch] = []

        used_by_others = {a["color"] for i2, a in enumerate(all_draft_agents) if i2 != index}

        self._name_field = ft.TextField(
            value=self._d["name"],
            label="Name",
            border_radius=8,
            border_color=BORDER,
            focused_border_color="#0084FF",
            text_size=13,
            on_change=self._on_name_change,
        )
        self._persona_field = ft.TextField(
            value=self._d["persona"],
            label="Persona / rules",
            multiline=True, min_lines=2, max_lines=5,
            border_radius=8, border_color=BORDER,
            focused_border_color="#0084FF", text_size=13,
            on_change=lambda e: self._update("persona", e.control.value),
        )
        self._source_dd = ft.Dropdown(
            value=self._d["source"], label="Source",
            border_radius=8, border_color=BORDER, focused_border_color="#0084FF",
            options=[
                ft.DropdownOption(key="claude", text="Claude API"),
                ft.DropdownOption(key="ollama", text="Ollama (local)"),
            ],
            on_select=lambda e: self._update("source", e.control.value),
        )
        self._length_dd = ft.Dropdown(
            value=self._d["response_length"], label="Response length",
            border_radius=8, border_color=BORDER, focused_border_color="#0084FF",
            options=[
                ft.DropdownOption(key="short", text="Short (1-2 sentences)"),
                ft.DropdownOption(key="medium", text="Medium (1 paragraph)"),
                ft.DropdownOption(key="long", text="Long (detailed)"),
            ],
            on_select=lambda e: self._update("response_length", e.control.value),
        )
        self._temp_label = ft.Text(
            f"Temperature: {self._d['temperature']:.1f}",
            size=FONT_SETTINGS_LABEL, color=TEXT_SECONDARY,
        )
        self._temp_slider = ft.Slider(
            value=self._d["temperature"], min=0.0, max=1.0, divisions=10,
            active_color="#0084FF", on_change=self._on_temp_change, expand=True,
        )
        self._enable_switch = ft.Switch(
            value=self._d["enabled"], active_color="#0084FF",
            on_change=self._on_enable_change,
        )

        swatch_row = self._build_swatch_row(self._d["color"], used_by_others)

        reset_btn = ft.TextButton(
            content=ft.Text("↺ Reset to default", size=11, color=TEXT_SECONDARY),
            on_click=self._handle_reset,
            style=ft.ButtonStyle(padding=ft.Padding(left=0, right=0, top=0, bottom=0)),
        )
        self._erase_btn = ft.TextButton(
            content=ft.Text("🗑 Erase memory", size=11, color="#C0392B"),
            on_click=self._handle_erase_memory,
            style=ft.ButtonStyle(padding=ft.Padding(left=0, right=0, top=0, bottom=0)),
        )

        tile_content = ft.Container(
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
                    ft.Divider(height=1, color=BORDER),
                    ft.Row(
                        controls=[reset_btn, ft.Container(expand=True), self._erase_btn],
                        spacing=0,
                    ),
                ],
                spacing=SPACE_SM,
            ),
            padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=SPACE_SM, bottom=SPACE_MD),
        )

        # Header: color dot + name + enabled badge (all visible before expand)
        self._header_dot = ft.Container(
            width=10, height=10,
            bgcolor=self._d["color"],
            border_radius=5,
        )
        self._header_name = ft.Text(
            self._d["name"], size=13, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY,
        )
        self._header_badge = self._make_badge(self._d["enabled"])

        header_row = ft.Row(
            controls=[
                self._header_dot,
                ft.Container(width=SPACE_SM),
                self._header_name,
                ft.Container(width=SPACE_XS),
                self._header_badge,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
            spacing=0,
        )

        super().__init__(
            title=header_row,
            controls=[tile_content],
            tile_padding=ft.Padding(left=SPACE_MD, right=SPACE_SM, top=0, bottom=0),
            collapsed_bgcolor=BG_SECONDARY if not self._d["enabled"] else BG_PRIMARY,
            bgcolor=BG_PRIMARY,
            text_color=TEXT_PRIMARY,
            icon_color=TEXT_SECONDARY,
        )

    def _make_badge(self, enabled: bool) -> ft.Container:
        return ft.Container(
            content=ft.Text(
                "ON" if enabled else "OFF",
                size=9,
                color="#FFFFFF" if enabled else TEXT_SECONDARY,
                weight=ft.FontWeight.W_700,
            ),
            bgcolor="#2DA44E" if enabled else "#E8E8E8",
            border_radius=4,
            padding=ft.Padding(left=5, right=5, top=2, bottom=2),
        )

    def _build_swatch_row(self, selected_color: str, used_by_others=None) -> ft.Row:
        if used_by_others is None:
            used_by_others = set()
        self._swatches = [
            _ColorSwatch(c, c == selected_color, c in used_by_others, self._on_color_pick)
            for c in AGENT_COLORS
        ]
        return ft.Row(controls=self._swatches, wrap=True, spacing=SPACE_SM, run_spacing=SPACE_SM)

    def update_taken_colors(self, used_by_others: set):
        """Called by parent panel whenever any agent's color changes."""
        current = self._d["color"]
        for sw in self._swatches:
            sw.set_state(selected=(sw._color == current), taken=(sw._color in used_by_others))

    # ── handlers ──────────────────────────────────────────────────────────────

    def _on_name_change(self, e):
        val = e.control.value
        self._update("name", val)
        self._header_name.value = val or f"Agent {self._index + 1}"
        self._header_name.update()

    def _on_enable_change(self, e):
        val = e.control.value
        self._update("enabled", val)
        self.collapsed_bgcolor = BG_SECONDARY if not val else BG_PRIMARY
        self._header_badge.content.value = "ON" if val else "OFF"
        self._header_badge.content.color = "#FFFFFF" if val else TEXT_SECONDARY
        self._header_badge.bgcolor = "#2DA44E" if val else "#E8E8E8"
        self._header_badge.update()
        self.update()

    def _on_color_pick(self, color: str):
        self._d["color"] = color
        self._on_change()       # mark dirty + show footer
        self._header_dot.bgcolor = color
        self._header_dot.update()
        if self._on_color_pick_cb:
            self._on_color_pick_cb()   # parent: sync_taken_colors + live_update

    def _on_temp_change(self, e):
        val = round(e.control.value, 1)
        self._temp_label.value = f"Temperature: {val:.1f}"
        self._temp_label.update()
        self._update("temperature", val)

    def _handle_reset(self, e):
        from data.settings_store import default_agent
        defaults = default_agent(self._index)
        self._d.update(defaults)
        # Refresh all controls
        self._name_field.value = defaults["name"]
        self._name_field.update()
        self._persona_field.value = defaults["persona"]
        self._persona_field.update()
        self._source_dd.value = defaults["source"]
        self._source_dd.update()
        self._length_dd.value = defaults["response_length"]
        self._length_dd.update()
        self._temp_slider.value = defaults["temperature"]
        self._temp_label.value = f"Temperature: {defaults['temperature']:.1f}"
        self._temp_slider.update()
        self._temp_label.update()
        self._enable_switch.value = defaults["enabled"]
        self._enable_switch.update()
        self._on_color_pick(defaults["color"])
        self._on_enable_change(type("E", (), {"control": self._enable_switch})())
        self._header_name.value = defaults["name"]
        self._header_name.update()
        self._on_change()

    def _handle_erase_memory(self, e):
        import os, shutil
        memory_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "agents", self._d["id"]
        )
        if os.path.exists(memory_dir):
            shutil.rmtree(memory_dir)
        self._erase_btn.content = ft.Text("✓ Memory erased", size=11, color="#2DA44E")
        self._erase_btn.update()
        if self.page:
            self.page.run_task(self._reset_erase_label)

    async def _reset_erase_label(self):
        import asyncio
        await asyncio.sleep(2.0)
        self._erase_btn.content = ft.Text("🗑 Erase memory", size=11, color="#C0392B")
        self._erase_btn.update()

    def _update(self, key: str, value):
        self._d[key] = value
        self._on_change()


class SettingsPanel(ft.Container):
    def __init__(self, on_close, on_save, on_live_update):
        self._on_close_cb = on_close
        self._on_save_cb = on_save
        self._on_live_update = on_live_update  # (draft: dict) → live preview in chat

        from data.settings_store import SettingsStore
        self._store = SettingsStore.instance()

        # Draft is a deep copy; original is snapshot at open time for cancel
        self._draft: dict = {}
        self._original: dict = {}
        self._has_changes = False

        # Build UI first (will be populated on open)
        self._body = self._build_body()
        self._footer = self._build_footer()
        self._header = self._build_header()

        super().__init__(
            content=ft.Column(
                controls=[self._header, self._body, self._footer],
                spacing=0,
                expand=True,
            ),
            width=PANEL_WIDTH,
            top=0, bottom=0, right=0,
            bgcolor=BG_PRIMARY,
            border=ft.border.Border(left=ft.BorderSide(1, BORDER)),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=24,
                color="#00000022", offset=ft.Offset(-4, 0),
            ),
            animate_offset=ft.Animation(ANIM_MS, ft.AnimationCurve.EASE_OUT),
            offset=ft.Offset(1, 0),
            visible=False,
        )

    # ── Build sections ────────────────────────────────────────────────────────

    def _build_header(self) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("Settings", size=FONT_SECTION_TITLE,
                            weight=ft.FontWeight.W_700, color=TEXT_PRIMARY),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE, icon_color=TEXT_SECONDARY,
                        icon_size=20, on_click=lambda e: self._handle_close(),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=SPACE_MD, right=SPACE_SM, top=0, bottom=0),
            height=48,
            border=ft.border.Border(bottom=ft.BorderSide(1, BORDER)),
        )

    def _build_body(self) -> ft.Column:
        # Appearance
        self._font_size_label = ft.Text("Font size: 14px", size=FONT_SETTINGS_LABEL, color=TEXT_SECONDARY)
        self._font_size_slider = ft.Slider(
            value=14.0, min=11, max=22, divisions=11,
            active_color="#0084FF", on_change=self._on_font_size_change, expand=True,
        )
        self._zoom_label = ft.Text("Zoom: 100%", size=FONT_SETTINGS_LABEL, color=TEXT_SECONDARY)
        self._zoom_slider = ft.Slider(
            value=100.0, min=75, max=150, divisions=15,
            active_color="#0084FF", on_change=self._on_zoom_change, expand=True,
        )
        self._font_dd = ft.Dropdown(
            value="Roboto", label="Font family",
            border_radius=8, border_color=BORDER, focused_border_color="#0084FF",
            options=[ft.DropdownOption(key=f, text=f) for f in CHAT_FONTS],
            on_select=self._on_font_change, expand=True,
        )

        appearance_section = ft.Column(controls=[
            _section_header("💬 Chat Appearance"),
            ft.Container(
                content=ft.Column(controls=[
                    self._font_size_label, self._font_size_slider,
                    self._zoom_label, self._zoom_slider,
                    self._font_dd,
                ], spacing=SPACE_XS),
                padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=0, bottom=SPACE_MD),
            ),
            _divider(),
        ], spacing=0)

        # Global
        self._api_key_field = ft.TextField(
            value="", label="Claude API key", password=True, can_reveal_password=True,
            border_radius=8, border_color=BORDER, focused_border_color="#0084FF", text_size=13,
            on_change=lambda e: self._update_draft(["global", "claude_api_key"], e.control.value),
        )
        self._ollama_field = ft.TextField(
            value="", label="Ollama URL",
            border_radius=8, border_color=BORDER, focused_border_color="#0084FF", text_size=13,
            on_change=lambda e: self._update_draft(["global", "ollama_url"], e.control.value),
        )
        self._agent_delay_label = ft.Text("Between agents: 2.0s", size=FONT_SETTINGS_LABEL, color=TEXT_SECONDARY)
        self._agent_delay_slider = ft.Slider(
            value=2.0, min=0.5, max=8.0, divisions=15,
            active_color="#0084FF", on_change=self._on_agent_delay_change, expand=True,
        )
        self._round_delay_label = ft.Text("Between rounds: 4.0s", size=FONT_SETTINGS_LABEL, color=TEXT_SECONDARY)
        self._round_delay_slider = ft.Slider(
            value=4.0, min=1.0, max=15.0, divisions=14,
            active_color="#0084FF", on_change=self._on_round_delay_change, expand=True,
        )

        global_section = ft.Column(controls=[
            _section_header("🌐 Global"),
            ft.Container(
                content=ft.Column(controls=[
                    self._api_key_field, self._ollama_field,
                    self._agent_delay_label, self._agent_delay_slider,
                    self._round_delay_label, self._round_delay_slider,
                ], spacing=SPACE_SM),
                padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=0, bottom=SPACE_MD),
            ),
            _divider(),
        ], spacing=0)

        # Agent tiles placeholder — filled in open()
        self._agents_col = ft.Column(controls=[], spacing=0)
        agents_section = ft.Column(controls=[
            _section_header("🤖 Agents"),
            self._agents_col,
        ], spacing=0)

        reset_all_btn = ft.Container(
            content=ft.Row(
                controls=[
                    ft.TextButton(
                        content=ft.Text("↺  Reset all settings to defaults",
                                        size=11, color=TEXT_SECONDARY),
                        on_click=self._handle_reset_all,
                        style=ft.ButtonStyle(
                            padding=ft.Padding(left=0, right=0, top=0, bottom=0),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
            padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=SPACE_SM, bottom=0),
        )

        return ft.Column(
            controls=[reset_all_btn, appearance_section, global_section, agents_section],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            expand=True,
        )

    def _build_footer(self) -> ft.Container:
        self._save_btn = ft.ElevatedButton(
            content=ft.Text("Save", color="#FFFFFF", size=13, weight=ft.FontWeight.W_600),
            bgcolor="#0084FF", elevation=0,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding(left=0, right=0, top=10, bottom=10),
                overlay_color="#FFFFFF26",
            ),
            expand=True,
            on_click=self._handle_save,
        )
        self._cancel_btn = ft.ElevatedButton(
            content=ft.Text("Cancel", color=TEXT_PRIMARY, size=13, weight=ft.FontWeight.W_600),
            bgcolor="#E8E8E8", elevation=0,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding(left=0, right=0, top=10, bottom=10),
                overlay_color="#00000010",
            ),
            expand=True,
            on_click=self._handle_cancel,
        )
        return ft.Container(
            content=ft.Row(
                controls=[self._cancel_btn, ft.Container(width=SPACE_SM), self._save_btn],
                spacing=0,
            ),
            bgcolor=FOOTER_BG,
            border=ft.border.Border(top=ft.BorderSide(1, BORDER)),
            padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=SPACE_SM, bottom=SPACE_MD),
            visible=False,
        )

    # ── Open / close ──────────────────────────────────────────────────────────

    def open(self):
        self._draft = copy.deepcopy(self._store._data)
        self._original = copy.deepcopy(self._store._data)
        self._has_changes = False
        self._sync_controls_from_draft()
        self.visible = True
        self.offset = ft.Offset(0, 0)
        self.update()

    def close(self):
        self.offset = ft.Offset(1, 0)
        self.update()
        if self.page:
            self.page.run_task(self._hide_after_anim)

    async def _hide_after_anim(self):
        import asyncio
        await asyncio.sleep(ANIM_MS / 1000 + 0.05)
        self.visible = False
        self.update()

    def _handle_close(self):
        if self._has_changes:
            self._do_cancel()
        self._on_close_cb()

    # ── Sync controls ↔ draft ─────────────────────────────────────────────────

    def _sync_controls_from_draft(self):
        app = self._draft.get("appearance", {})
        fs = app.get("font_size", 14)
        zoom = app.get("zoom", 1.0)
        font = app.get("font_family", "Roboto")

        self._font_size_label.value = f"Font size: {fs}px"
        self._font_size_slider.value = float(fs)
        self._zoom_label.value = f"Zoom: {int(zoom * 100)}%"
        self._zoom_slider.value = zoom * 100
        self._font_dd.value = font

        glb = self._draft.get("global", {})
        self._api_key_field.value = glb.get("claude_api_key", "")
        self._ollama_field.value = glb.get("ollama_url", "http://localhost:11434")
        self._agent_delay_label.value = f"Between agents: {glb.get('inter_agent_delay', 2.0):.1f}s"
        self._agent_delay_slider.value = glb.get("inter_agent_delay", 2.0)
        self._round_delay_label.value = f"Between rounds: {glb.get('inter_round_delay', 4.0):.1f}s"
        self._round_delay_slider.value = glb.get("inter_round_delay", 4.0)

        # Rebuild agent tiles from draft (each tile knows all agents to show taken colors)
        all_agents = self._draft["agents"]
        self._agents_col.controls = [
            _AgentTile(
                index=i,
                draft_agent=all_agents[i],
                all_draft_agents=all_agents,
                on_change=self._mark_has_changes,
                on_color_pick=self._on_any_color_change,
            )
            for i in range(5)
        ]

        self._footer.visible = False

    # ── Dirty tracking ────────────────────────────────────────────────────────

    def _mark_has_changes(self):
        if not self._has_changes:
            self._has_changes = True
            self._footer.visible = True
            self._footer.update()

    def _update_draft(self, path: list, value):
        node = self._draft
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        self._mark_has_changes()

    # ── Appearance handlers ───────────────────────────────────────────────────

    def _on_font_size_change(self, e):
        val = int(e.control.value)
        self._font_size_label.value = f"Font size: {val}px"
        self._font_size_label.update()
        self._update_draft(["appearance", "font_size"], val)
        self._preview_appearance()

    def _on_zoom_change(self, e):
        pct = int(e.control.value)
        self._zoom_label.value = f"Zoom: {pct}%"
        self._zoom_label.update()
        self._update_draft(["appearance", "zoom"], pct / 100)
        self._preview_appearance()

    def _on_font_change(self, e):
        self._update_draft(["appearance", "font_family"], e.control.value)
        self._preview_appearance()

    def _preview_appearance(self):
        self._on_live_update(self._draft)

    # ── Global handlers ───────────────────────────────────────────────────────

    def _on_agent_delay_change(self, e):
        val = round(e.control.value, 1)
        self._agent_delay_label.value = f"Between agents: {val:.1f}s"
        self._agent_delay_label.update()
        self._update_draft(["global", "inter_agent_delay"], val)

    def _on_round_delay_change(self, e):
        val = round(e.control.value, 1)
        self._round_delay_label.value = f"Between rounds: {val:.1f}s"
        self._round_delay_label.update()
        self._update_draft(["global", "inter_round_delay"], val)

    # ── Save / Cancel ─────────────────────────────────────────────────────────

    def _handle_save(self, e):
        self._store._data = copy.deepcopy(self._draft)
        self._store.save()
        self._has_changes = False
        self._footer.visible = False
        self._footer.update()
        self._on_save_cb(self._store)
        self._on_close_cb()

    def _handle_cancel(self, e):
        self._do_cancel()
        self._on_close_cb()

    def _do_cancel(self):
        self._draft = copy.deepcopy(self._original)
        self._has_changes = False
        self._footer.visible = False
        self._on_live_update(self._original)  # revert chat to original appearance + agent colors

    # ── Color change coordination ─────────────────────────────────────────────

    def _on_any_color_change(self):
        """Called by any agent tile when its color changes. Syncs taken-state across all tiles."""
        self._sync_taken_colors()
        self._on_live_update(self._draft)

    def _sync_taken_colors(self):
        tiles = [c for c in self._agents_col.controls if isinstance(c, _AgentTile)]
        for i, tile in enumerate(tiles):
            used = {self._draft["agents"][j]["color"]
                    for j in range(len(self._draft["agents"])) if j != i}
            tile.update_taken_colors(used)

    def _handle_reset_all(self, e):
        from data.settings_store import default_settings
        self._draft = default_settings()
        self._has_changes = False       # reset so _mark_has_changes will trigger
        self._sync_controls_from_draft()
        self._mark_has_changes()        # show Save/Cancel
        self._on_live_update(self._draft)
        if self.page:
            self.page.update()
