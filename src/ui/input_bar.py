import flet as ft
from ui.theme import (
    BG_SECONDARY, BG_PRIMARY, BORDER, SEND_BTN,
    TEXT_SECONDARY, TEXT_INVERSE,
    INPUT_BAR_HEIGHT, FONT_INPUT, SPACE_SM, SPACE_MD
)


class InputBar(ft.Container):
    """Bottom bar with text field and send button."""

    def __init__(self, on_send: callable):
        self._on_send = on_send
        self._disabled = False

        self._field = ft.TextField(
            hint_text="Message...",
            hint_style=ft.TextStyle(color=TEXT_SECONDARY),
            border_radius=24,
            border_color=BORDER,
            focused_border_color=SEND_BTN,
            border_width=1.5,
            focused_border_width=1.5,
            bgcolor=BG_PRIMARY,
            content_padding=ft.padding.symmetric(horizontal=20, vertical=12),
            text_size=FONT_INPUT,
            multiline=True,
            min_lines=1,
            max_lines=4,
            expand=True,
            on_submit=self._handle_send,
            shift_enter=True,   # Shift+Enter adds newline; Enter alone sends
        )

        self._send_btn = ft.Container(
            content=ft.Icon(ft.icons.SEND_ROUNDED, color=TEXT_INVERSE, size=20),
            bgcolor=SEND_BTN,
            border_radius=24,
            width=48,
            height=48,
            alignment=ft.alignment.center,
            on_click=self._handle_send,
            animate_scale=ft.Animation(80, ft.AnimationCurve.EASE_IN_OUT),
        )

        super().__init__(
            content=ft.Row(
                controls=[self._field, ft.Container(width=SPACE_SM), self._send_btn],
                vertical_alignment=ft.CrossAxisAlignment.END,
                spacing=0,
            ),
            height=INPUT_BAR_HEIGHT,
            bgcolor=BG_SECONDARY,
            border=ft.border.only(top=ft.BorderSide(1, BORDER)),
            padding=ft.padding.symmetric(horizontal=SPACE_MD, vertical=12),
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def set_disabled(self, disabled: bool, hint: str = ""):
        self._disabled = disabled
        self._field.disabled = disabled
        self._field.hint_text = hint if hint else ("Message..." if not disabled else "Waiting for agents...")
        self._send_btn.opacity = 0.4 if disabled else 1.0
        self.update()

    def clear(self):
        self._field.value = ""
        self._field.update()

    def focus(self):
        self._field.focus()

    # ── Internals ─────────────────────────────────────────────────────────────

    def _handle_send(self, e):
        if self._disabled:
            return
        text = (self._field.value or "").strip()
        if not text:
            return
        self.clear()
        self._on_send(text)
