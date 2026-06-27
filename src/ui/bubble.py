import flet as ft
from ui.theme import (
    USER_BUBBLE, TEXT_INVERSE, TEXT_SECONDARY,
    BUBBLE_PADDING_H, BUBBLE_PADDING_V,
    BUBBLE_RADIUS, BUBBLE_RADIUS_CORNER,
    BUBBLE_MAX_WIDTH, BUBBLE_SHADOW_BLUR, BUBBLE_SHADOW_COLOR,
    FONT_BUBBLE, FONT_AGENT_NAME, FONT_TIMESTAMP,
    SPACE_XS, SPACE_SM, ANIM_BUBBLE_MS,
)


def _shadow():
    return ft.BoxShadow(
        spread_radius=0,
        blur_radius=BUBBLE_SHADOW_BLUR,
        color=BUBBLE_SHADOW_COLOR,
        offset=ft.Offset(0, 1),
    )


def _bubble_pad():
    return ft.Padding(
        left=BUBBLE_PADDING_H, right=BUBBLE_PADDING_H,
        top=BUBBLE_PADDING_V, bottom=BUBBLE_PADDING_V,
    )


class UserBubble(ft.Container):
    def __init__(self, content: str, timestamp: str = ""):
        bubble = ft.Container(
            content=ft.Text(content, color=TEXT_INVERSE, size=FONT_BUBBLE, selectable=True),
            bgcolor=USER_BUBBLE,
            border_radius=ft.BorderRadius(
                top_left=BUBBLE_RADIUS, top_right=BUBBLE_RADIUS,
                bottom_left=BUBBLE_RADIUS, bottom_right=BUBBLE_RADIUS_CORNER,
            ),
            padding=_bubble_pad(),
            shadow=_shadow(),
            max_width=BUBBLE_MAX_WIDTH,
            animate_opacity=ft.Animation(ANIM_BUBBLE_MS, ft.AnimationCurve.EASE_OUT),
            animate_offset=ft.Animation(ANIM_BUBBLE_MS, ft.AnimationCurve.EASE_OUT),
            offset=ft.Offset(0, 0.3),
            opacity=0,
        )

        col_controls = [bubble]
        if timestamp:
            col_controls.append(ft.Text(timestamp, size=FONT_TIMESTAMP, color=TEXT_SECONDARY))

        col = ft.Column(
            controls=col_controls,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            tight=True, spacing=SPACE_XS,
        )

        super().__init__(
            content=ft.Row(controls=[col], alignment=ft.MainAxisAlignment.END),
            padding=ft.Padding(left=80, right=SPACE_SM, top=2, bottom=2),
        )
        self._bubble = bubble

    def did_mount(self):
        self._bubble.opacity = 1
        self._bubble.offset = ft.Offset(0, 0)
        self._bubble.update()


class AgentBubble(ft.Container):
    def __init__(
        self,
        content: str,
        agent_name: str,
        agent_color: str,
        show_name: bool = True,
        timestamp: str = "",
        has_thought: bool = False,
        on_show_thought: callable = None,
    ):
        bubble = ft.Container(
            content=ft.Text(content, color=TEXT_INVERSE, size=FONT_BUBBLE, selectable=True),
            bgcolor=agent_color,
            border_radius=ft.BorderRadius(
                top_left=BUBBLE_RADIUS_CORNER if show_name else BUBBLE_RADIUS,
                top_right=BUBBLE_RADIUS,
                bottom_left=BUBBLE_RADIUS,
                bottom_right=BUBBLE_RADIUS,
            ),
            padding=_bubble_pad(),
            shadow=_shadow(),
            max_width=BUBBLE_MAX_WIDTH,
            animate_opacity=ft.Animation(ANIM_BUBBLE_MS, ft.AnimationCurve.EASE_OUT),
            animate_offset=ft.Animation(ANIM_BUBBLE_MS, ft.AnimationCurve.EASE_OUT),
            offset=ft.Offset(0, 0.3),
            opacity=0,
        )

        controls = []
        if show_name:
            controls.append(
                ft.Row(
                    controls=[
                        ft.Container(width=8, height=8, bgcolor=agent_color, border_radius=4),
                        ft.Text(agent_name, size=FONT_AGENT_NAME, weight=ft.FontWeight.W_600, color=agent_color),
                    ],
                    tight=True, spacing=SPACE_XS,
                )
            )
        controls.append(bubble)
        if timestamp:
            controls.append(ft.Text(timestamp, size=FONT_TIMESTAMP, color=TEXT_SECONDARY))
        if has_thought and on_show_thought:
            controls.append(
                ft.TextButton(
                    content=ft.Text("💭 Show thought", size=11, color=agent_color),
                    on_click=lambda e: on_show_thought(),
                    style=ft.ButtonStyle(padding=ft.Padding(left=0, right=0, top=0, bottom=0)),
                )
            )

        super().__init__(
            content=ft.Row(
                controls=[ft.Column(controls=controls, tight=True, spacing=SPACE_XS)],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.Padding(left=SPACE_SM, right=80, top=2, bottom=2),
        )
        self._bubble = bubble

    def did_mount(self):
        self._bubble.opacity = 1
        self._bubble.offset = ft.Offset(0, 0)
        self._bubble.update()


class SystemMessage(ft.Container):
    def __init__(self, text: str):
        super().__init__(
            content=ft.Row(
                controls=[
                    ft.Divider(height=1, color="#E8E8E8"),
                    ft.Container(
                        content=ft.Text(text, size=11, color=TEXT_SECONDARY),
                        padding=ft.Padding(left=SPACE_SM, right=SPACE_SM, top=0, bottom=0),
                    ),
                    ft.Divider(height=1, color="#E8E8E8"),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=0, right=0, top=SPACE_SM, bottom=SPACE_SM),
        )
