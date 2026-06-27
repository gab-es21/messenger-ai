import os
import traceback
import flet as ft

from utils.logger import get_logger
from ui.chat_window import ChatWindow
from ui.theme import BG_PRIMARY, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT

log = get_logger(__name__)

_ICON_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")


def main(page: ft.Page):
    log.info("main() called — setting up page")
    try:
        page.title = "Round Table"
        page.bgcolor = BG_PRIMARY
        page.padding = 0
        page.spacing = 0

        page.window.title_bar_hidden = True
        page.window.width = WINDOW_WIDTH
        page.window.height = WINDOW_HEIGHT
        page.window.min_width = WINDOW_MIN_WIDTH
        page.window.min_height = WINDOW_MIN_HEIGHT
        if os.path.exists(_ICON_PATH):
            page.window.icon = os.path.abspath(_ICON_PATH)

        page.theme = ft.Theme(font_family="Roboto")

        log.info("Adding ChatWindow to page")
        page.add(ChatWindow())
        page.update()
        log.info("Page ready")

    except Exception:
        log.error("Fatal error during page setup:\n%s", traceback.format_exc())
        raise


if __name__ == "__main__":
    log.info("Launching Round Table via ft.run()")
    ft.run(main)
