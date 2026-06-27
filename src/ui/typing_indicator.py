import asyncio
import flet as ft
from ui.theme import (
    DOT_SIZE, DOT_SPACING, DOT_BOUNCE_PX,
    DOT_ANIM_MS, DOT_CYCLE_MS, DOT_DELAYS,
    FONT_AGENT_NAME, BUBBLE_RADIUS, BUBBLE_RADIUS_CORNER,
    SPACE_XS
)


class TypingIndicator(ft.Container):
    """
    Three bouncing dots in a bubble, shown while an agent is generating.
    Call start() when the agent begins and stop() when first text chunk arrives.
    """

    def __init__(self, agent_name: str, agent_color: str):
        self._agent_name = agent_name
        self._agent_color = agent_color
        self._running = False

        dot_color = agent_color
        # 20% opacity background approximated with hex alpha
        bubble_bg = agent_color + "33"

        self._dots = [
            ft.Container(
                width=DOT_SIZE,
                height=DOT_SIZE,
                bgcolor=dot_color,
                border_radius=DOT_SIZE // 2,
                animate_offset=ft.Animation(DOT_ANIM_MS, ft.AnimationCurve.EASE_IN_OUT),
                offset=ft.Offset(0, 0),
            )
            for _ in range(3)
        ]

        dot_row = ft.Row(controls=self._dots, spacing=DOT_SPACING, tight=True)

        bubble = ft.Container(
            content=dot_row,
            bgcolor=bubble_bg,
            border_radius=ft.BorderRadius(
                top_left=BUBBLE_RADIUS_CORNER,
                top_right=BUBBLE_RADIUS,
                bottom_left=BUBBLE_RADIUS,
                bottom_right=BUBBLE_RADIUS,
            ),
            padding=ft.padding.symmetric(horizontal=14, vertical=12),
            width=64,
        )

        name_row = ft.Row(
            controls=[
                ft.Container(width=8, height=8, bgcolor=agent_color, border_radius=4),
                ft.Text(agent_name, size=FONT_AGENT_NAME, weight=ft.FontWeight.W_600, color=agent_color),
            ],
            tight=True,
            spacing=SPACE_XS,
        )

        col = ft.Column(controls=[name_row, bubble], tight=True, spacing=SPACE_XS)

        super().__init__(
            content=ft.Row(controls=[col], alignment=ft.MainAxisAlignment.START),
            padding=ft.padding.only(left=8, right=80, top=2, bottom=2),
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
        for dot in self._dots:
            dot.offset = ft.Offset(0, 0)
            dot.update()

    async def _animate_loop(self):
        while self._running:
            for dot, delay in zip(self._dots, DOT_DELAYS):
                self.page.run_task(self._bounce_dot, dot, delay)
            await asyncio.sleep(DOT_CYCLE_MS / 1000)

    async def _bounce_dot(self, dot: ft.Container, delay: float):
        await asyncio.sleep(delay)
        if not self._running:
            return
        # offset is a fraction of the control's own size
        # DOT_BOUNCE_PX / DOT_SIZE gives the fractional offset
        dot.offset = ft.Offset(0, -(DOT_BOUNCE_PX / DOT_SIZE))
        dot.update()
        await asyncio.sleep(DOT_ANIM_MS / 1000)
        if not self._running:
            return
        dot.offset = ft.Offset(0, 0)
        dot.update()
