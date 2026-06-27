import flet as ft
from ui.theme import BG_PRIMARY, TEXT_SECONDARY, SPACE_MD


class EmptyState(ft.Container):
    def __init__(self):
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text("💬", size=48),
                    ft.Text("Start a brainstorm", size=16, weight=ft.FontWeight.W_600, color="#1A1A1A"),
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
            alignment=ft.Alignment(0, 0),
            expand=True,
        )


class ChatArea(ft.Container):
    def __init__(self):
        self._list = ft.ListView(
            expand=True,
            spacing=4,
            padding=ft.Padding(left=SPACE_MD, right=SPACE_MD, top=12, bottom=12),
            auto_scroll=True,
        )
        self._empty = EmptyState()
        self._has_messages = False

        super().__init__(
            content=ft.Stack(controls=[self._empty, self._list], expand=True),
            expand=True,
            bgcolor=BG_PRIMARY,
        )

    def add(self, control: ft.Control):
        if not self._has_messages:
            self._has_messages = True
            self._empty.visible = False
            self._empty.update()
        self._list.controls.append(control)
        self._list.update()

    def remove(self, control: ft.Control):
        if control in self._list.controls:
            self._list.controls.remove(control)
            self._list.update()

    def replace(self, old: ft.Control, new: ft.Control):
        if old in self._list.controls:
            idx = self._list.controls.index(old)
            self._list.controls[idx] = new
            self._list.update()

    def clear(self):
        self._list.controls.clear()
        self._has_messages = False
        self._empty.visible = True
        self._list.update()
        self._empty.update()
