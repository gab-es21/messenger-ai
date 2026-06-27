import flet as ft
from ui.theme import BG_PRIMARY, TEXT_SECONDARY, SPACE_MD


class EmptyState(ft.Container):
    """Shown when there are no messages yet."""

    def __init__(self):
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text("💬", size=48),
                    ft.Text(
                        "Start a brainstorm",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color="#1A1A1A",
                    ),
                    ft.Text(
                        "Type a message below, or press Start\nto let agents talk on their own.",
                        size=13,
                        color=TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=SPACE_MD,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )


class ChatArea(ft.Container):
    """
    Scrollable message list.
    Add controls via add() — handles auto-scroll and empty-state toggling.
    """

    def __init__(self):
        self._list = ft.ListView(
            expand=True,
            spacing=4,
            padding=ft.padding.symmetric(horizontal=SPACE_MD, vertical=12),
            auto_scroll=True,
        )
        self._empty = EmptyState()
        self._has_messages = False

        super().__init__(
            content=ft.Stack(
                controls=[self._empty, self._list],
                expand=True,
            ),
            expand=True,
            bgcolor=BG_PRIMARY,
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def add(self, control: ft.Control):
        """Append a bubble, indicator, or system message and scroll into view."""
        if not self._has_messages:
            self._has_messages = True
            self._empty.visible = False
            self._empty.update()

        self._list.controls.append(control)
        self._list.update()

    def remove(self, control: ft.Control):
        """Remove a control (e.g. swap typing indicator for real bubble)."""
        if control in self._list.controls:
            self._list.controls.remove(control)
            self._list.update()

    def clear(self):
        self._list.controls.clear()
        self._has_messages = False
        self._empty.visible = True
        self._list.update()
        self._empty.update()

    def scroll_to_bottom(self):
        self._list.scroll_to(offset=-1, duration=200)
