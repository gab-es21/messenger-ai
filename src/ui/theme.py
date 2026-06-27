"""Visual design tokens — single source of truth for all colors, sizes, and spacing."""

# ── Background ──────────────────────────────────────────────────────────────
BG_PRIMARY = "#FFFFFF"
BG_SECONDARY = "#F5F5F5"
BG_CONTROL_BAR = "#FAFAFA"

# ── Text ────────────────────────────────────────────────────────────────────
TEXT_PRIMARY = "#1A1A1A"
TEXT_SECONDARY = "#8A8A8A"
TEXT_INVERSE = "#FFFFFF"

# ── Borders & Shadows ───────────────────────────────────────────────────────
BORDER = "#E8E8E8"
SHADOW = "#00000014"  # rgba(0,0,0,0.08) as hex with alpha

# ── Accent ──────────────────────────────────────────────────────────────────
USER_BUBBLE = "#0084FF"
USER_BUBBLE_HOVER = "#006FD6"
SEND_BTN = "#0084FF"

# ── Status ──────────────────────────────────────────────────────────────────
SUCCESS = "#00C851"
ERROR = "#FF4444"
WARNING = "#FFA500"
INFO = "#0084FF"

# ── Agent color pool (index 0-5) ─────────────────────────────────────────────
AGENT_COLORS = [
    "#FF6B6B",  # Coral
    "#4ECDC4",  # Teal
    "#9B8EC4",  # Lavender
    "#6BAE8E",  # Sage
    "#E8A838",  # Amber
    "#5A7FA8",  # Slate
]

# ── Layout ───────────────────────────────────────────────────────────────────
TITLE_BAR_HEIGHT = 48
CONTROL_BAR_HEIGHT = 44
INPUT_BAR_HEIGHT = 72

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 700
WINDOW_MIN_HEIGHT = 500

# ── Bubble ───────────────────────────────────────────────────────────────────
BUBBLE_PADDING_H = 16
BUBBLE_PADDING_V = 12
BUBBLE_RADIUS = 18
BUBBLE_RADIUS_CORNER = 4      # the corner closest to the sender name
BUBBLE_MAX_WIDTH = 520        # px — ~65% of 900 default window
BUBBLE_SHADOW_BLUR = 3
BUBBLE_SHADOW_COLOR = "#0000001F"  # rgba(0,0,0,0.12)

# ── Typography ───────────────────────────────────────────────────────────────
FONT_BUBBLE = 14
FONT_AGENT_NAME = 11
FONT_TIMESTAMP = 11
FONT_INPUT = 14
FONT_SETTINGS_LABEL = 12
FONT_SETTINGS_HEADER = 13
FONT_SECTION_TITLE = 15

# ── Spacing ──────────────────────────────────────────────────────────────────
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 16
SPACE_LG = 24
SPACE_XL = 32

# ── Typing indicator ─────────────────────────────────────────────────────────
DOT_SIZE = 8
DOT_SPACING = 6
DOT_BOUNCE_PX = 6      # pixels the dot travels up
DOT_ANIM_MS = 300      # duration of one bounce leg
DOT_CYCLE_MS = 900     # full cycle (all 3 dots)
DOT_DELAYS = [0.0, 0.16, 0.32]  # stagger in seconds

# ── Animation ────────────────────────────────────────────────────────────────
ANIM_BUBBLE_MS = 200
ANIM_SETTINGS_OPEN_MS = 280
ANIM_SETTINGS_CLOSE_MS = 220
ANIM_TOAST_MS = 200
