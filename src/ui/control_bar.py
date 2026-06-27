import asyncio
import flet as ft
from ui.theme import (
    BG_CONTROL_BAR, BORDER, TEXT_SECONDARY,
    CONTROL_BAR_HEIGHT, SUCCESS, ERROR, WARNING,
)


class ControlBar(ft.Container):
    def __init__(self, on_start: callable, on_stop: callable):
        self._on_start = on_start
        self._on_stop = on_stop
        self._mode = "idle"

        self._start_btn = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color="#FFFFFF", size=16),
                    ft.Text("Start", color="#FFFFFF", size=13, weight=ft.FontWeight.W_600),
                ],
                tight=True, spacing=4,
            ),
            bgcolor=SUCCESS,
            elevation=0,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                overlay_color="#FFFFFF26",
            ),
            on_click=self._handle_click,
        )

        self._status_dot = ft.Container(
            width=8, height=8,
            bgcolor=TEXT_SECONDARY,
            border_radius=4,
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
        )

        self._status_text = ft.Text(
            "Agents are idle — press Start to begin",
            size=12, color=TEXT_SECONDARY,
        )
        self._round_label = ft.Text("", size=12, color=TEXT_SECONDARY)

        super().__init__(
            content=ft.Row(
                controls=[
                    self._start_btn,
                    ft.Container(width=12),
                    ft.Row(
                        controls=[self._status_dot, ft.Container(width=6), self._status_text],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        tight=True,
                    ),
                    ft.Container(expand=True),
                    self._round_label,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            height=CONTROL_BAR_HEIGHT,
            bgcolor=BG_CONTROL_BAR,
            border=ft.border.Border(
                top=ft.BorderSide(1, BORDER),
                bottom=ft.BorderSide(1, BORDER),
            ),
            padding=ft.Padding(left=16, right=16, top=0, bottom=0),
        )

    def set_running(self, round_num: int = 1):
        self._mode = "running"
        self._start_btn.content = ft.Row(
            controls=[
                ft.Icon(ft.Icons.STOP_ROUNDED, color="#FFFFFF", size=16),
                ft.Text("Stop", color="#FFFFFF", size=13, weight=ft.FontWeight.W_600),
            ],
            tight=True, spacing=4,
        )
        self._start_btn.bgcolor = ERROR
        self._status_dot.bgcolor = SUCCESS
        self._status_text.value = "Agents are talking..."
        self._round_label.value = f"Round {round_num}"
        self.update()
        if self.page:
            self.page.run_task(self._pulse_dot)

    def set_stopping(self):
        self._mode = "stopping"
        self._start_btn.disabled = True
        self._status_dot.bgcolor = WARNING
        self._status_text.value = "Finishing current response..."
        self._round_label.value = ""
        self.update()

    def set_idle(self):
        self._mode = "idle"
        self._start_btn.disabled = False
        self._start_btn.content = ft.Row(
            controls=[
                ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color="#FFFFFF", size=16),
                ft.Text("Start", color="#FFFFFF", size=13, weight=ft.FontWeight.W_600),
            ],
            tight=True, spacing=4,
        )
        self._start_btn.bgcolor = SUCCESS
        self._status_dot.bgcolor = TEXT_SECONDARY
        self._status_text.value = "Agents are idle — press Start to begin"
        self._round_label.value = ""
        self.update()

    def set_agent_active(self, agent_name: str, round_num: int):
        self._status_text.value = f"{agent_name} is thinking..."
        self._round_label.value = f"Round {round_num}"
        self.update()

    def _handle_click(self, e):
        if self._mode == "idle":
            self._on_start()
        elif self._mode == "running":
            self._on_stop()

    async def _pulse_dot(self):
        while self._mode == "running":
            self._status_dot.opacity = 0.3
            self._status_dot.update()
            await asyncio.sleep(0.6)
            self._status_dot.opacity = 1.0
            self._status_dot.update()
            await asyncio.sleep(0.6)
