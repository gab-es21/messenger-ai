import asyncio
import flet as ft
from ui.theme import (
    DOT_SIZE, DOT_SPACING, DOT_BOUNCE_PX,
    DOT_ANIM_MS, DOT_CYCLE_MS, DOT_DELAYS,
    FONT_AGENT_NAME, BUBBLE_RADIUS, BUBBLE_RADIUS_CORNER, SPACE_XS,
)


class TypingIndicator(ft.Container):
    """Three bouncing dots in an agent-colored bubble."""

    def __init__(self, agent_name: str, agent_color: str):
        self._agent_name = agent_name
        self._agent_color = agent_color
        self._running = False

        self._dots = [
            ft.Container(
                width=DOT_SIZE, height=DOT_SIZE,
                bgcolor=agent_color,
                border_radius=DOT_SIZE // 2,
                animate_offset=ft.Animation(DOT_ANIM_MS, ft.AnimationCurve.EASE_IN_OUT),
                offset=ft.Offset(0, 0),
            )
            for _ in range(3)
        ]

        bubble = ft.Container(
            content=ft.Row(controls=self._dots, spacing=DOT_SPACING, tight=True),
            bgcolor=agent_color + "33",
            border_radius=ft.BorderRadius(
                top_left=BUBBLE_RADIUS_CORNER, top_right=BUBBLE_RADIUS,
                bottom_left=BUBBLE_RADIUS, bottom_right=BUBBLE_RADIUS,
            ),
            padding=ft.Padding(left=14, right=14, top=12, bottom=12),
            width=64,
        )

        name_row = ft.Row(
            controls=[
                ft.Container(width=8, height=8, bgcolor=agent_color, border_radius=4),
                ft.Text(agent_name, size=FONT_AGENT_NAME, weight=ft.FontWeight.W_600, color=agent_color),
            ],
            tight=True, spacing=SPACE_XS,
        )

        col = ft.Column(controls=[name_row, bubble], tight=True, spacing=SPACE_XS)

        super().__init__(
            content=ft.Row(controls=[col], alignment=ft.MainAxisAlignment.START),
            padding=ft.Padding(left=8, right=80, top=2, bottom=2),
            animate_opacity=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            opacity=0,
        )

    def did_mount(self):
        self.opacity = 1
        self.update()
        self.start()

    def will_unmount(self):
        self._running = False

    def start(self):
        self._running = True
        if self.page:
            self.page.run_task(self._animate_loop)

    def stop(self):
        self._running = False

    async def _animate_loop(self):
        while self._running:
            for dot, delay in zip(self._dots, DOT_DELAYS):
                self.page.run_task(self._bounce_dot, dot, delay)
            await asyncio.sleep(DOT_CYCLE_MS / 1000)

    async def _bounce_dot(self, dot: ft.Container, delay: float):
        await asyncio.sleep(delay)
        if not self._running:
            return
        dot.offset = ft.Offset(0, -(DOT_BOUNCE_PX / DOT_SIZE))
        dot.update()
        await asyncio.sleep(DOT_ANIM_MS / 1000)
        if not self._running:
            return
        dot.offset = ft.Offset(0, 0)
        dot.update()
