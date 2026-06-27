import flet as ft
from ui.theme import (
    BG_PRIMARY, BORDER, TEXT_PRIMARY, TEXT_SECONDARY,
    TITLE_BAR_HEIGHT, FONT_SECTION_TITLE,
)


class TitleBar(ft.Container):
    def __init__(
        self,
        on_settings: callable,
        on_toggle_thoughts: callable,
        on_clear_chat: callable,
        thoughts_on: bool = True,
    ):
        self._on_settings = on_settings
        self._on_toggle_thoughts = on_toggle_thoughts
        self._on_clear_chat = on_clear_chat
        self._thoughts_on = thoughts_on

        self._thoughts_btn = ft.IconButton(
            icon=ft.Icons.BUBBLE_CHART,
            icon_color="#0084FF" if thoughts_on else TEXT_SECONDARY,
            icon_size=20,
            tooltip="Toggle thoughts panel",
            on_click=self._handle_thoughts,
        )

        self._clear_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=TEXT_SECONDARY,
            icon_size=20,
            tooltip="Clear chat (keeps agent memories)",
            on_click=self._handle_clear,
        )

        self._settings_btn = ft.IconButton(
            icon=ft.Icons.SETTINGS_OUTLINED,
            icon_color=TEXT_SECONDARY,
            icon_size=20,
            tooltip="Settings",
            on_click=self._handle_settings,
        )

        drag_area = ft.WindowDragArea(
            content=ft.Row(
                controls=[ft.Text("Roundtable", size=FONT_SECTION_TITLE, weight=ft.FontWeight.W_700, color=TEXT_PRIMARY)],
            ),
            expand=True,
        )

        close_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_color=TEXT_SECONDARY,
            icon_size=18,
            tooltip="Close",
            on_click=lambda e: e.page.window.close(),
        )

        super().__init__(
            content=ft.Row(
                controls=[drag_area, self._thoughts_btn, self._clear_btn, self._settings_btn, close_btn],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            height=TITLE_BAR_HEIGHT,
            bgcolor=BG_PRIMARY,
            border=ft.border.Border(bottom=ft.BorderSide(1, BORDER)),
            padding=ft.Padding(left=16, right=4, top=0, bottom=0),
        )

    def _handle_thoughts(self, e):
        self._thoughts_on = not self._thoughts_on
        self._thoughts_btn.icon_color = "#0084FF" if self._thoughts_on else TEXT_SECONDARY
        self._thoughts_btn.update()
        self._on_toggle_thoughts(self._thoughts_on)

    def _handle_settings(self, e):
        self._settings_btn.icon_color = "#0084FF"
        self._settings_btn.update()
        self._on_settings()

    def _handle_clear(self, e):
        self._on_clear_chat()
