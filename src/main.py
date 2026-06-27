import flet as ft
from ui.chat_window import ChatWindow
from ui.theme import BG_PRIMARY, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT


def main(page: ft.Page):
    # ── Window setup ──────────────────────────────────────────────────────────
    page.title = "Prism"
    page.bgcolor = BG_PRIMARY
    page.padding = 0
    page.spacing = 0

    # Hide OS title bar so our custom one takes over
    page.window.title_bar_hidden = True
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.window.min_width = WINDOW_MIN_WIDTH
    page.window.min_height = WINDOW_MIN_HEIGHT

    # Smooth font rendering
    page.fonts = {}
    page.theme = ft.Theme(font_family="Roboto")

    page.add(ChatWindow())
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
