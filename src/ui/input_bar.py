import flet as ft
from ui.theme import (
    BG_SECONDARY, BG_PRIMARY, BORDER, SEND_BTN,
    TEXT_SECONDARY, TEXT_INVERSE,
    INPUT_BAR_HEIGHT, FONT_INPUT, SPACE_SM, SPACE_MD,
)


class InputBar(ft.Container):
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
            content_padding=ft.Padding(left=20, right=20, top=12, bottom=12),
            text_size=FONT_INPUT,
            color="#1A1A1A",
            multiline=True,
            min_lines=1,
            max_lines=3,
            expand=True,
            on_submit=self._handle_send,
            shift_enter=True,
        )

        self._send_btn = ft.Container(
            content=ft.Icon(ft.Icons.SEND_ROUNDED, color=TEXT_INVERSE, size=20),
            bgcolor=SEND_BTN,
            border_radius=24,
            width=48, height=48,
            alignment=ft.Alignment(0, 0),
            on_click=self._handle_send,
            animate_scale=ft.Animation(80, ft.AnimationCurve.EASE_IN_OUT),
        )

        super().__init__(
            content=ft.Row(
                controls=[self._field, ft.Container(width=SPACE_SM), self._send_btn],
                vertical_alignment=ft.CrossAxisAlignment.END,
                spacing=0,
            ),
            bgcolor=BG_SECONDARY,
            border=ft.border.Border(top=ft.BorderSide(1, BORDER)),
            padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=12, bottom=12),
        )

    def set_disabled(self, disabled: bool, hint: str = ""):
        self._disabled = disabled
        self._field.disabled = disabled
        self._field.hint_text = hint or ("Waiting for agents..." if disabled else "Message...")
        self._send_btn.opacity = 0.4 if disabled else 1.0
        self.update()

    def clear(self):
        self._field.value = ""
        self._field.update()

    def focus(self):
        self._field.focus()

    def _handle_send(self, e):
        if self._disabled:
            return
        text = (self._field.value or "").strip()
        if not text:
            return
        self.clear()
        self._on_send(text)
