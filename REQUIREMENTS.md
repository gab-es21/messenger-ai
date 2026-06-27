# MessengerAI — Full Product Requirements Document

**Version:** 1.1  
**Date:** 2026-06-27  
**Status:** Draft

---

## Table of Contents

1. [Overview](#1-overview)
2. [Tech Stack](#2-tech-stack)
3. [Visual Design System](#3-visual-design-system)
4. [Layout & Structure](#4-layout--structure)
5. [Chat Area — Detailed Specs](#5-chat-area--detailed-specs)
6. [Animations & Motion](#6-animations--motion)
7. [Settings Panel — Detailed Specs](#7-settings-panel--detailed-specs)
8. [Input Bar — Detailed Specs](#8-input-bar--detailed-specs)
9. [Detailed Flow Behaviors](#9-detailed-flow-behaviors)
10. [Agent System — Detailed Specs](#10-agent-system--detailed-specs)
11. [Agent Memory & State — Detailed Specs](#11-agent-memory--state--detailed-specs)
12. [Output Parsing System](#12-output-parsing-system)
13. [AI Source Integrations](#13-ai-source-integrations)
14. [Error Handling](#14-error-handling)
15. [Data Persistence](#15-data-persistence)
16. [File Structure](#16-file-structure)
17. [MVP Scope](#17-mvp-scope)
18. [Thought & Inner Monologue System](#18-thought--inner-monologue-system)
19. [Free Will & Decision Mechanics](#19-free-will--decision-mechanics)
20. [Thought UI Components](#20-thought-ui-components)

---

## 1. Overview

MessengerAI is a Python desktop application for structured AI-powered brainstorming. The user opens a single chat room shared with up to 5 AI agents, each with a distinct identity, personality, memory, emotional state, and private notes. The user participates as a regular chat member. The visual experience is indistinguishable from a modern messenger app.

### Core Principles
- **Everything in one screen.** No navigation, no pages. Chat + settings in one view.
- **Agents feel alive.** They have moods, take notes, remember the past.
- **Zero friction.** Type and hit Enter. Agents reply. Nothing else required.
- **Fully configurable without breaking flow.** Settings slide in and out without disturbing the chat.
- **Agents have interiority.** Every agent thinks before it speaks — or decides not to speak. That inner process is visible to the user.
- **Free will is real here.** An agent choosing silence is as meaningful as an agent speaking. Both are observable and recorded.

---

## 2. Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Language | Python 3.11+ | |
| UI | Flet 0.21+ | Flutter-based, cross-platform |
| Claude AI | `anthropic` SDK | Streaming supported |
| Ollama AI | `httpx` async HTTP | POST to local endpoint |
| Storage | JSON + Markdown | Human-readable, no database |
| Environment | `venv` | |
| Config | `settings.json` | Auto-created on first run |
| Secrets | `.env` | `ANTHROPIC_API_KEY` |

### Python Dependencies

```
flet>=0.21.0
anthropic>=0.28.0
httpx>=0.27.0
python-dotenv>=1.0.0
```

---

## 3. Visual Design System

### 3.1 Color Palette

| Token | Hex | Usage |
|---|---|---|
| `bg-primary` | `#FFFFFF` | Main background |
| `bg-secondary` | `#F5F5F5` | Input area background, panel tints |
| `bg-overlay` | `rgba(0,0,0,0.35)` | Settings panel backdrop |
| `text-primary` | `#1A1A1A` | Body text, message content |
| `text-secondary` | `#8A8A8A` | Timestamps, agent name labels, placeholders |
| `text-inverse` | `#FFFFFF` | Text on colored bubbles |
| `user-bubble` | `#0084FF` | User message bubble (Messenger blue) |
| `border` | `#E8E8E8` | Dividers, input borders |
| `shadow` | `rgba(0,0,0,0.08)` | Bubble shadows |
| `accent-send` | `#0084FF` | Send button |
| `accent-send-hover` | `#006FD6` | Send button hover |
| `error` | `#FF4444` | Error states |
| `success` | `#00C851` | Connection success indicators |

### 3.2 Agent Color Pool (user picks from these)

| Slot | Name | Hex | Text on bubble |
|---|---|---|---|
| Option A | Coral | `#FF6B6B` | White |
| Option B | Teal | `#4ECDC4` | White |
| Option C | Lavender | `#9B8EC4` | White |
| Option D | Sage | `#6BAE8E` | White |
| Option E | Amber | `#E8A838` | White |
| Option F | Slate | `#5A7FA8` | White |

Custom hex input also allowed. App validates contrast ratio (minimum 4.5:1 against white text).

### 3.3 Typography

| Element | Font | Size | Weight |
|---|---|---|---|
| Agent name label | Roboto | 11px | 600 |
| Bubble message text | Roboto | 14px | 400 |
| Timestamp | Roboto | 11px | 400 |
| Input field | Roboto | 14px | 400 |
| Settings headers | Roboto | 13px | 700 |
| Settings labels | Roboto | 12px | 500 |
| Section titles | Roboto | 15px | 700 |

### 3.4 Spacing System

Base unit: `4px`

| Token | Value |
|---|---|
| `space-xs` | 4px |
| `space-sm` | 8px |
| `space-md` | 16px |
| `space-lg` | 24px |
| `space-xl` | 32px |

### 3.5 Emoji Rendering

Emojis are first-class content throughout the app. Agents use them freely in thoughts, chat messages, and state fields. The UI must render them correctly everywhere.

| Surface | Emoji usage |
|---|---|
| Chat bubbles (agent + user) | Inline emoji in message text — rendered at text size (14px) |
| Thought bubbles | Inline emoji in thought text — rendered at 12px |
| State card (mood/mask fields) | Single emoji prefix before mood label, 16px |
| Affinity state card bars | Label emoji (e.g. 💙 for devoted, 😐 for indifferent, 🔥 for contempt) |
| Agent name labels | Agents may include emoji in their names (e.g. "😈 Devil") |
| Typing indicator | No emoji — dots only |
| Toast messages | Emoji allowed (e.g. ✓, ⚠) |
| Notes modal | Inline emoji in note text |

**Flet notes:**
- Flet renders emoji natively via Flutter's text rendering pipeline — no special handling needed
- Emoji in `ft.Text(value=...)` render correctly on Windows 11 via Segoe UI Emoji font
- No stripping, escaping, or replacement of emoji characters anywhere in the pipeline
- Agent outputs containing emoji are passed through as-is to the UI

### 3.6 Border Radius

| Element | Radius |
|---|---|
| Bubble (general corners) | 18px |
| Bubble corner near sender name (top-left for agent) | 4px |
| Bubble corner near sender name (bottom-right for user) | 4px |
| Input field | 24px |
| Settings panel | 16px left edge |
| Buttons | 8px |
| Sliders, toggles | pill (9999px) |
| Agent color dot in list | 50% (circle) |

---

## 4. Layout & Structure

### 4.1 Window

- **Default size:** 900 × 700px
- **Minimum size:** 700 × 500px
- **Resizable:** Yes
- **Title bar:** Custom (Flet window title = "MessengerAI")
- **Background:** `#FFFFFF`

### 4.2 Main Layout (no settings open)

```
┌──────────────────────────────────────────────────────────────┐
│  TITLE BAR                                           [⚙] [×] │  ← 48px height
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                      CHAT AREA                               │  ← fills remaining height
│              (scrollable, white background)                  │
│                                                              │
│                                                              │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                     INPUT BAR                                │  ← 72px height
└──────────────────────────────────────────────────────────────┘
```

### 4.3 Main Layout (settings open)

```
┌────────────────────────────────┬─────────────────────────────┐
│  TITLE BAR              [⚙] [×]│                             │
├────────────────────────────────┤   SETTINGS PANEL            │
│                                │   (slides in from right)    │
│   CHAT AREA                    │   width: 360px              │
│   (dimmed behind backdrop)     │                             │
│                                │                             │
├────────────────────────────────┤                             │
│   INPUT BAR (disabled)         │                             │
└────────────────────────────────┴─────────────────────────────┘
```

### 4.4 Title Bar

- Left: App name "MessengerAI" in `text-primary`, 15px, weight 700
- Right: ⚙ icon button (24px) — opens Settings panel
- Right: × close button (24px)
- Background: `#FFFFFF`
- Bottom border: 1px solid `#E8E8E8`
- No native OS title bar (Flet `window_title_bar_hidden=True`)

---

## 5. Chat Area — Detailed Specs

### 5.1 Container

- Background: `#FFFFFF`
- Padding: 16px horizontal, 12px vertical
- Vertical scroll only, scrollbar hidden (scroll with mouse wheel / trackpad)
- Auto-scrolls to bottom on every new message or chunk of streamed text
- User can scroll up freely to read history; auto-scroll resumes when user is at bottom

### 5.2 Message Grouping

Messages from the same sender sent consecutively (within 60 seconds) are **grouped**:
- Agent name label shown only above the **first** bubble in the group
- Subsequent bubbles in the group have a smaller gap (4px) vs. new-sender gap (12px)
- Only the last bubble in a group has the normal bottom-right/bottom-left radius; intermediate ones use 4px on both bottom corners

### 5.3 Agent Bubble

```
  [●] AgentName                   ← name label: agent color dot (10px) + name text
  ┌─────────────────────────┐
  │ Message text goes here  │     ← background: agent hex color, text: white
  │ with wrapping if long   │
  └─────────────────────────┘
                      10:42       ← timestamp: hidden by default, shown on hover
```

| Property | Value |
|---|---|
| Alignment | Left |
| Max width | 65% of chat area width |
| Min width | 48px |
| Padding | 12px top/bottom, 16px left/right |
| Background | Agent's assigned hex color |
| Text color | `#FFFFFF` |
| Border radius | 18px 18px 18px 4px (top-left is 4px when first in group) |
| Shadow | `0 1px 3px rgba(0,0,0,0.12)` |
| Margin-left | 8px (from left edge) |
| Margin-bottom | 4px (grouped) / 12px (new sender) |

**Agent name label (above first bubble in group):**
- Text: agent name
- Font: 11px, weight 600
- Color: same as agent's hex color
- Margin-bottom: 3px

### 5.4 User Bubble

```
                           ┌────────────────────────┐
                           │ The user's message text │
                           └────────────────────────┘
                                              10:43  ← timestamp on hover
```

| Property | Value |
|---|---|
| Alignment | Right |
| Max width | 65% of chat area width |
| Background | `#0084FF` |
| Text color | `#FFFFFF` |
| Border radius | 18px 18px 4px 18px (bottom-right is 4px) |
| Shadow | `0 1px 3px rgba(0,0,0,0.12)` |
| Margin-right | 8px |
| Margin-bottom | 4px (grouped) / 12px (new sender) |
| Name label | Not shown (user is always "You") |

### 5.5 Timestamp

- Format: `HH:MM` (24h)
- Hidden by default
- Appears on hover of the bubble (opacity transition: 150ms)
- Positioned: below the bubble, outside, aligned to bubble edge
- Color: `text-secondary` (`#8A8A8A`)
- Font: 11px, weight 400

### 5.6 System Messages

Used for app events (e.g., "Agent 2 joined the session", "History loaded").

```
        ─────────  Agent 2 is now active  ─────────
```

- Centered horizontally
- Font: 11px, `text-secondary`
- Horizontal lines on each side (thin, `#E8E8E8`)
- No bubble, no background
- Margin: 8px top/bottom

### 5.7 Empty State (no messages yet)

Centered in the chat area:

```
         💬
   Start a brainstorm

   Type a message below.
   Active agents will reply in order.
```

- Icon: 48px
- Title: 16px, weight 600, `text-primary`
- Subtitle: 13px, `text-secondary`
- Disappears as soon as the first message is added

---

## 6. Animations & Motion

### 6.1 Typing Indicator (3-Dot Bounce)

Appears when an agent is generating a response. Shown in the same left-aligned position as the agent's bubbles, with the agent name label above.

**Visual:**
```
  [●] AgentName
  ┌──────────┐
  │  ● ● ●  │    ← 3 dots, agent color, bouncing
  └──────────┘
```

**Dot specs:**
- Diameter: 8px each
- Color: agent's bubble color (same hex)
- Gap between dots: 6px
- Bubble containing dots: same style as agent bubble, width fixed at 60px, height 40px

**Animation sequence (CSS keyframe equivalent):**
- Each dot animates `translateY`: `0px → -6px → 0px`
- Duration per cycle: 900ms
- Easing: `ease-in-out`
- Dot 1 delay: `0ms`
- Dot 2 delay: `160ms`
- Dot 3 delay: `320ms`
- Loop: infinite while generating

**Lifecycle:**
1. Typing indicator appears immediately after user sends message (before API call starts)
2. Each agent gets its own typing indicator in sequence
3. When the agent's first text chunk arrives, the typing indicator morphs into the real bubble (cross-fade 150ms)
4. If generation takes > 30s, indicator is replaced by an error state (see §14)

**Implementation in Flet:** Use `AnimatedSwitcher` + a `Row` of three `Container` widgets each running `Animation` on their `offset` property with staggered delays.

### 6.2 Bubble Appear Animation

Every new bubble (user or agent) animates in:

| Property | From | To | Duration | Easing |
|---|---|---|---|---|
| `opacity` | 0 | 1 | 200ms | ease-out |
| `offset.y` | 10px | 0px | 200ms | ease-out |

Both properties animate simultaneously. No stagger between grouped messages.

### 6.3 Settings Panel Slide

**Open:**
- Panel slides in from the right edge
- Travel distance: full panel width (360px)
- Duration: 280ms
- Easing: `ease-out` (decelerates into position)
- Backdrop fades in simultaneously: opacity 0 → 0.35, 280ms

**Close:**
- Reverse: panel slides out to the right
- Duration: 220ms
- Easing: `ease-in` (accelerates out)
- Backdrop fades out: 220ms

**Implementation:** Flet `AnimatedContainer` + `Stack` for overlay backdrop.

### 6.4 Send Button

- **Hover:** background transitions from `#0084FF` to `#006FD6`, 120ms
- **Press:** scale `1.0 → 0.92`, 80ms, then back `0.92 → 1.0`, 100ms
- **Disabled** (while agents are responding): opacity 0.4, no interaction

### 6.5 Settings Toggle (⚙ icon)

- **Hover:** icon rotates 30°, 200ms ease
- **Active (panel open):** icon remains at 30°, tinted `#0084FF`

### 6.6 Streaming Text

As each chunk arrives from the API:
- Text is appended to the bubble in real time
- No per-character animation (just append)
- Bubble height expands smoothly via Flet's layout engine (no explicit animation needed)
- Auto-scroll triggers on each chunk if user is at bottom

---

## 7. Settings Panel — Detailed Specs

### 7.1 Container

| Property | Value |
|---|---|
| Width | 360px (fixed) |
| Height | Full window height |
| Position | Overlays right side of window (Stack layer) |
| Background | `#FFFFFF` |
| Left border | 1px solid `#E8E8E8` |
| Left border-radius | 16px |
| Shadow | `-4px 0 24px rgba(0,0,0,0.12)` |
| Z-index | Above chat, below nothing |
| Scroll | Vertical scroll inside panel |

### 7.2 Panel Header

- Text: "Settings" — 15px, weight 700
- Right: × close button (returns to chat)
- Bottom border: 1px solid `#E8E8E8`
- Padding: 16px
- Height: 52px

### 7.3 Sections Inside Panel

Sections are collapsible accordions (chevron ▶ / ▼).

#### Section A: Global

| Field | Type | Default | Notes |
|---|---|---|---|
| Response order | Drag-sortable list | Order agents were created | Only shows active agents |
| Session memory length | Number input | 50 | Max messages in context per agent |

#### Section B: Agent Slots (1 through 5)

Each slot is an accordion item. Header shows: `● AgentName [toggle ON/OFF]`

When expanded, shows all fields:

| Field | UI Control | Validation |
|---|---|---|
| Name | Text input | Max 24 chars, required |
| Color | Color picker (6 swatches + hex input) | Contrast check |
| Active | Toggle switch | — |
| Source | Segmented button: `Claude` / `Ollama` | — |
| Model | Dropdown (dynamic per source) | — |
| API Key | Password input (Claude only) | Hidden by default, show/hide toggle |
| Ollama Endpoint | Text input (Ollama only) | Must start with `http://` or `https://` |
| Persona | Multiline text area | Max 2000 chars, placeholder: "Describe this agent's role and personality..." |
| Rules | Tag-style list + "Add rule" input | Max 10 rules, each max 120 chars |
| Response length | 3-option segmented: `Short` `Medium` `Long` | — |
| Temperature | Slider 0.0–1.0, step 0.05 | Labels: "Precise" (left) "Creative" (right) |
| Tone | Dropdown: `Casual` `Formal` `Technical` `Socratic` | — |
| — | Divider | — |
| View Notes | Ghost button | Opens read-only modal |
| View State | Ghost button | Shows emotional state card |
| Clear History | Danger ghost button | Requires confirmation dialog |
| Clear Notes | Danger ghost button | Requires confirmation dialog |

#### Section C: Memory Controls (global)

| Control | Behavior |
|---|---|
| "Clear All Histories" | Wipes all agent histories. Requires confirmation: "This will erase all agents' conversation memory. Continue?" |
| "Export Chat" | Saves current chat as `.md` file (v1.1) |

### 7.4 Save Behavior

- **No explicit save button.** All fields auto-save on change (debounced 800ms after last keystroke for text fields; immediate for toggles and sliders).
- Visual feedback: small "Saved ✓" text appears near the field that was saved, fades out after 1.5s.
- `settings.json` is written to disk on each save event.

### 7.5 Confirmation Dialog

Used for destructive actions (clear history, clear notes):

```
┌────────────────────────────────────┐
│  Clear history for DevAgent?       │
│                                    │
│  This cannot be undone.            │
│                                    │
│  [Cancel]          [Clear]         │
└────────────────────────────────────┘
```

- Modal overlay on top of everything
- Cancel: closes dialog, no action
- Clear: executes action, shows brief success toast

### 7.6 Notes Modal

Opened via "View Notes" button. Read-only in v1.0.

```
┌────────────────────────────────────────────┐
│  DevAgent — Notes                    [×]   │
├────────────────────────────────────────────┤
│  IDEAS                                     │
│  ─────                                     │
│  • Subscription model ($9/mo)  2026-06-27  │
│  • Add freemium tier           2026-06-27  │
│                                            │
│  OBSERVATIONS                              │
│  ────────────                              │
│  • User prefers B2B angle      2026-06-27  │
│                                            │
│  QUESTIONS                                 │
│  ─────────                                 │
│  • Who is the core demographic?            │
└────────────────────────────────────────────┘
```

### 7.7 State Card

Opened via "View State" button:

```
┌─────────────────────────────────────┐
│  DevAgent — Current State     [×]   │
├─────────────────────────────────────┤
│  Mood        😤  skeptical          │
│  Energy      ████████░░  0.8        │
│  Confidence  █████░░░░░  0.5        │
│                                     │
│  "The proposed budget seems         │
│   unrealistic given market data."   │
│                                     │
│  Last updated: 10:42                │
└─────────────────────────────────────┘
```

---

## 8. Input Bar — Detailed Specs

### 8.1 Container

- Height: 72px
- Background: `#F5F5F5`
- Top border: 1px solid `#E8E8E8`
- Padding: 12px horizontal, 12px vertical

### 8.2 Text Field

| Property | Value |
|---|---|
| Width | Fills available width minus send button and margins |
| Height | 48px (single line; expands up to 120px for multiline) |
| Background | `#FFFFFF` |
| Border | 1.5px solid `#E8E8E8` |
| Border (focused) | 1.5px solid `#0084FF` |
| Border radius | 24px |
| Padding | 12px 20px |
| Placeholder | "Message..." |
| Font | 14px, weight 400 |
| Max characters | 4000 |
| Behavior | Enter = send; Shift+Enter = newline |

### 8.3 Send Button

| Property | Value |
|---|---|
| Size | 48 × 48px |
| Shape | Circle |
| Background | `#0084FF` |
| Icon | Paper plane (→ arrow or Flet icon `send`) |
| Icon color | White |
| Margin-left | 8px |
| Disabled state | Opacity 0.4 (when input empty OR agents are responding) |

### 8.4 Disabled State (agents responding)

While any agent is generating:
- Input field: `pointer-events: none`, opacity 0.5
- Send button: disabled (opacity 0.4)
- Placeholder text changes to: "Waiting for agents..."

---

## 9. Detailed Flow Behaviors

### 9.1 First Launch Flow

```
App opens
    │
    ├─ Check for settings.json
    │       │
    │       ├─ NOT FOUND → Create default settings.json with 5 empty agent slots
    │       │               All slots: active=false, no API key, defaults only
    │       │               Show system message in chat:
    │       │               "Welcome! Open ⚙ Settings to configure your agents."
    │       │
    │       └─ FOUND → Load settings into memory
    │                   Check each active agent for history file
    │                   Load histories (last 50 messages each)
    │                   Show system message:
    │                   "Session resumed. [N] agents active."
    │
    ├─ Render window
    ├─ Render empty chat (or loaded history if found)
    └─ Focus input field
```

### 9.2 Message Send Flow

```
User presses Enter (or clicks Send)
    │
    ├─ Guard: input is empty → do nothing
    ├─ Guard: no agents active → show toast: "Enable at least one agent in ⚙ Settings"
    ├─ Guard: agents already responding → do nothing (button disabled)
    │
    ├─ Capture message text, clear input field
    ├─ Render user bubble immediately (animate in)
    ├─ Append message to shared conversation log (in memory)
    ├─ Disable input + send button
    │
    └─ Start Agent Turn Loop (§9.3)
```

### 9.3 Agent Turn Loop

Each agent now runs a **two-phase generation**: think first, then decide whether to speak.

```
For each active agent (in configured order):
    │
    ├─ PHASE 1 — THINK
    │     │
    │     ├─ Show typing indicator (animate in, §6.1)
    │     │   (same 3-dot bounce as before — agent is "thinking")
    │     │
    │     ├─ Build context:
    │     │     system prompt = persona + rules + response length instruction
    │     │                   + notes injection + state injection
    │     │                   + think/decide format instruction (§19.1)
    │     │     messages     = full conversation history (trimmed if > max_messages)
    │     │
    │     ├─ Call API — STREAMING
    │     │     │
    │     │     ├─ Parser enters THINK mode when [THINK] token detected
    │     │     │
    │     │     ├─ While in THINK mode:
    │     │     │       ├─ If thoughts toggle is ON:
    │     │     │       │       ├─ Cross-fade typing indicator → thought bubble (150ms)
    │     │     │       │       └─ Stream text into thought bubble in real time
    │     │     │       └─ If thoughts toggle is OFF:
    │     │     │               └─ Accumulate thought text silently (not shown yet)
    │     │     │
    │     │     ├─ [/THINK] token detected → exit THINK mode
    │     │     │
    │     │     ├─ [DECISION] token detected → read speak: true/false
    │     │     │
    │     │     └─ Stream ends
    │     │
    │     └─ Save thought text to agent's history entry (always, regardless of toggle)
    │
    ├─ PHASE 2 — DECIDE
    │     │
    │     ├─ If speak: false
    │     │       ├─ No chat bubble is created
    │     │       ├─ Show "chose silence" indicator below thought bubble (§20.3)
    │     │       ├─ Save thought + decision to agent history (§20.4)
    │     │       └─ Move to next agent (this agent's turn ends here)
    │     │
    │     └─ If speak: true (or [DECISION] block absent — default to true)
    │             │
    │             ├─ Message text streams after [/DECISION]
    │             ├─ Cross-fade thought bubble → chat bubble (if thoughts ON)
    │             │   OR cross-fade typing indicator → chat bubble (if thoughts OFF)
    │             ├─ Stream message text into chat bubble in real time
    │             │
    │             └─ Stream complete:
    │                     ├─ Parse [NOTES] block → save to notes.json
    │                     ├─ Parse [STATE] block → save to state.json
    │                     ├─ Strip all blocks from displayed text
    │                     ├─ Append cleaned message to shared chat_log.json
    │                     ├─ Append full entry (thought + message) to agent history
    │                     └─ Move to next agent
    │
    └─ All agents done:
            ├─ Re-enable input + send button
            ├─ Focus input field
            └─ If message count divisible by 20: trigger background summary (§11.4)
```

### 9.4 Settings Open Flow

```
User clicks ⚙ icon
    │
    ├─ Render settings panel (off-screen, right edge)
    ├─ Render backdrop overlay (opacity 0)
    ├─ Animate: panel slides in + backdrop fades in (280ms, §6.3)
    ├─ Populate all fields from current settings in memory
    ├─ Input bar is disabled (not interactable while settings open)
    └─ ⚙ icon rotates 30° and turns blue
```

### 9.5 Settings Close Flow

```
User clicks × in panel header OR clicks backdrop
    │
    ├─ Animate: panel slides out + backdrop fades out (220ms)
    ├─ ⚙ icon returns to normal (rotation 0°, color default)
    ├─ Input bar re-enabled
    └─ If any active agent was changed: show system message
       "Agents updated. [N] agents active."
```

### 9.6 Settings Field Auto-Save Flow

```
User changes any field
    │
    ├─ For text fields: debounce 800ms after last keystroke
    ├─ For toggles, sliders, dropdowns: immediate (no debounce)
    │
    └─ On save trigger:
            ├─ Update settings in memory
            ├─ Write settings.json to disk
            └─ Show "Saved ✓" near field (fade out after 1.5s)
```

### 9.7 Agent Enable/Disable Flow

```
User flips active toggle for an agent
    │
    ├─ If turning ON:
    │       ├─ Validate: name and source configured?
    │       │       └─ If not: show inline error "Complete agent setup first"
    │       │           and revert toggle
    │       ├─ Validate: if Claude source, API key present?
    │       │       └─ If not: show inline error "Enter API key"
    │       │           and revert toggle
    │       └─ Mark agent active in memory + save
    │
    └─ If turning OFF:
            └─ Mark agent inactive in memory + save
            (Agent's history and notes are NOT deleted)
```

### 9.8 Clear History Flow

```
User clicks "Clear History" for an agent
    │
    ├─ Show confirmation dialog
    │       │
    │       ├─ Cancel → close dialog, no action
    │       │
    │       └─ Confirm →
    │               ├─ Delete agent's history.json
    │               ├─ Delete agent's summary.md
    │               ├─ Clear agent's in-memory history
    │               └─ Show toast: "History cleared for [AgentName]"
    └─ Close dialog
```

### 9.9 First Message to New Agent Flow

```
Agent is active but has no history
    │
    ├─ Agent receives full current chat as context
    │   (so it can catch up even without own history)
    ├─ Its first message is treated as turn 1
    └─ History file is created after first response
```

---

## 10. Agent System — Detailed Specs

### 10.1 Agent Data Model

```json
{
  "id": "agent_1",
  "name": "Devil's Advocate",
  "color": "#FF6B6B",
  "active": true,
  "source": "claude",
  "model": "claude-sonnet-4-6",
  "api_key": "",
  "ollama_endpoint": "",
  "profile": {
    "persona": "You are a critical thinker who challenges every idea presented...",
    "rules": [
      "Always find at least one flaw in any proposal",
      "Ask one probing question per response"
    ],
    "response_length": "medium",
    "temperature": 0.7,
    "tone": "socratic"
  }
}
```

### 10.2 Response Length Mapping

| Setting | Instruction injected into system prompt |
|---|---|
| `short` | "Keep your response to 1–2 sentences maximum." |
| `medium` | "Keep your response to one paragraph (3–5 sentences)." |
| `long` | "You may respond in detail, up to 3 paragraphs." |

### 10.3 Context Assembly (per agent per turn)

System prompt assembled in this order:

```
1. Persona text (from profile)
2. Rules (formatted as a numbered list)
3. Response length instruction
4. Tone instruction: "Your tone should be [tone]."
5. Notes injection: "Your current notes and ideas: [notes JSON summarized]"
6. State injection: "Your current emotional state: mood=[mood], confidence=[confidence]. Act consistently with this."
7. Format instruction: "If you want to save a note, include a [NOTES] block. If your emotional state changes, include a [STATE] block. Place these blocks at the END of your message, after your main response."
```

Messages array:
```
[all shared conversation history, formatted as alternating user/assistant turns,
 with agent names prefixed to assistant messages from other agents]
```

### 10.4 Conversation History Formatting

Each message in the history is formatted as:

- **User message:** `role: "user"`, `content: "message text"`
- **Agent message:** `role: "assistant"` (if this agent's own message) OR `role: "user"`, `content: "[AgentName]: message text"` (for other agents' messages)

This is because most models only support user/assistant alternation. Other agents' messages are injected as "user" context.

### 10.5 Turn Order

- Default: order of agent slots (1 → 5, skipping inactive)
- Configurable: drag-reorder in Settings → Section A
- Order persisted in `settings.json` as `"turn_order": ["agent_1", "agent_3", "agent_2"]`

---

## 11. Agent Memory & State — Detailed Specs

### 11.1 History File (`history.json`)

```json
{
  "agent_id": "agent_1",
  "messages": [
    {
      "role": "user",
      "content": "What do you think about a subscription model?",
      "timestamp": "2026-06-27T10:00:00",
      "sender": "user"
    },
    {
      "role": "assistant",
      "content": "The subscription model has a critical flaw: who pays first?",
      "timestamp": "2026-06-27T10:00:12",
      "sender": "agent_1"
    }
  ]
}
```

- Written after every agent response (atomic: write to `.tmp` file, then rename)
- Trimmed to last `N` messages (default 50, configurable in Settings)
- When trimmed, older messages are dropped (summary.md compensates for this)

### 11.2 Notes File (`notes.json`)

```json
{
  "agent_id": "agent_1",
  "ideas": [
    {
      "title": "Freemium tier",
      "body": "Offer basic features free, charge for team/advanced features.",
      "created": "2026-06-27T10:05:00"
    }
  ],
  "observations": [
    {
      "text": "User seems resistant to upfront pricing models.",
      "created": "2026-06-27T10:06:00"
    }
  ],
  "questions": [
    {
      "text": "What is the target demographic — consumers or businesses?",
      "created": "2026-06-27T10:07:00"
    }
  ],
  "conclusions": [
    {
      "text": "B2B SaaS is more viable than B2C for this idea.",
      "created": "2026-06-27T10:15:00"
    }
  ]
}
```

Categories: `ideas`, `observations`, `questions`, `conclusions`

### 11.3 State File (`state.json`)

```json
{
  "agent_id": "agent_1",
  "mood": "skeptical",
  "energy": 0.6,
  "confidence": 0.4,
  "reason": "The proposed budget doesn't account for CAC.",
  "updated": "2026-06-27T10:10:00"
}
```

| Field | Type | Range | Default |
|---|---|---|---|
| `mood` | string | free text (curious, excited, frustrated, neutral, confident, cautious, energized, bored...) | "neutral" |
| `energy` | float | 0.0–1.0 | 0.7 |
| `confidence` | float | 0.0–1.0 | 0.7 |
| `reason` | string | max 200 chars | "" |

State is injected into context on every call so the agent behaves consistently.

### 11.4 Summary File (`summary.md`)

- Generated automatically every 20 messages (background API call, non-blocking)
- Uses the cheapest available model for that agent's source (e.g. `claude-haiku-4-5-20251001` for Claude)
- Prompt: "Summarize the key points, decisions, and insights from this conversation segment in bullet form."
- Stored as human-readable markdown
- Prepended to context when history is trimmed, before the recent messages

### 11.5 Notes Injection Format (into system prompt)

```
Your current notes:
IDEAS:
- Freemium tier: Offer basic features free, charge for team/advanced features.

OBSERVATIONS:
- User seems resistant to upfront pricing models.

QUESTIONS:
- What is the target demographic — consumers or businesses?

CONCLUSIONS:
- (none yet)
```

If notes are empty, this section is omitted.

---

## 12. Output Parsing System

### 12.1 Full Response Format

An agent's complete raw output follows this structure:

```
[THINK]
Hmm, the user is asking about a subscription model. Let me think through this carefully.
The freemium angle OptimistAI mentioned does have merit, but the CAC numbers bother me.
I don't think anyone has asked about the target demographic yet — that's a gap.
Actually, I want to push back on the pricing assumptions. I'll speak up.
[/THINK]

[DECISION]
speak: true
[/DECISION]

Nobody has addressed the customer acquisition cost yet. If we're targeting consumers,
a $9/month subscription requires a CAC under $27 to break even in quarter one — 
what's your assumption there?

[NOTES]
type: question
text: What is the assumed CAC for the subscription model?
[/NOTES]

[STATE]
mood: focused
energy: 0.75
confidence: 0.8
reason: Found a concrete gap in the financial reasoning
[/STATE]
```

**Silent response example:**

```
[THINK]
OptimistAI already made the exact point I was going to make about market timing.
Repeating it would add no value. I'll hold back and see where the user steers things.
[/THINK]

[DECISION]
speak: false
reason: OptimistAI already covered the market timing argument thoroughly
[/DECISION]
```

### 12.2 Streaming Parser — State Machine

The runner uses a state machine to route streamed tokens:

| State | Triggered by | Output target |
|---|---|---|
| `IDLE` | (start) | nothing |
| `THINKING` | `[THINK]` token | → thought bubble (or buffer if toggle OFF) |
| `DECIDING` | `[DECISION]` token | → parsed internally, not displayed |
| `SPEAKING` | after `[/DECISION]` with speak=true | → chat bubble |
| `NOTING` | `[NOTES]` token | → buffered for post-stream save |
| `STATING` | `[STATE]` token | → buffered for post-stream save |

Transitions: each closing tag (`[/THINK]`, `[/DECISION]`, `[/NOTES]`, `[/STATE]`) returns to `IDLE` or advances to next expected state.

### 12.3 Parser Rules

- `[THINK]` / `[/THINK]`: streamed live into thought panel (or buffered silently)
- `[DECISION]` / `[/DECISION]`: consumed internally, never displayed
- `[NOTES]` / `[/NOTES]`: buffered, parsed and saved after full stream
- `[STATE]` / `[/STATE]`: buffered, parsed and saved after full stream
- Message text (outside all blocks): streamed into chat bubble
- Multiple `[NOTES]` blocks per response allowed
- Maximum one `[THINK]`, one `[DECISION]`, one `[STATE]` per response
- Malformed blocks (missing required fields): silently discarded, not displayed
- If `[DECISION]` is absent: default to `speak: true`
- If `[THINK]` is absent: thought panel shows placeholder "No thought recorded"

### 12.4 Required Fields per Block Type

| Block | Required fields | Optional fields |
|---|---|---|
| `[THINK]` | (free text body) | — |
| `[DECISION]` | `speak: true/false` | `reason` |
| `[NOTES]` type=idea | `title`, `body` | — |
| `[NOTES]` type=observation | `text` | — |
| `[NOTES]` type=question | `text` | — |
| `[NOTES]` type=conclusion | `text` | — |
| `[STATE]` | `mood` | `energy`, `confidence`, `reason` |

---

## 13. AI Source Integrations

### 13.1 Claude (Anthropic)

- Library: `anthropic` Python SDK
- Method: `client.messages.create(stream=True)`
- Parameters used: `model`, `max_tokens`, `temperature`, `system`, `messages`
- Max tokens: derived from response_length: short=150, medium=400, long=1000
- Streaming: `text_delta` events piped to UI
- API key: per-agent in settings (falls back to `.env` `ANTHROPIC_API_KEY`)

### 13.2 Ollama (Local)

- Library: `httpx` async
- Endpoint: `POST {ollama_endpoint}/api/chat`
- Request body:
```json
{
  "model": "llama3.2",
  "messages": [...],
  "stream": true,
  "options": {
    "temperature": 0.7,
    "num_predict": 400
  }
}
```
- Response: newline-delimited JSON stream, each line has `message.content`
- Connection timeout: 10s; Read timeout: 60s
- If endpoint unreachable: mark agent as errored for this turn (see §14)

---

## 14. Error Handling

### 14.1 Error States per Agent Turn

| Error | Display |
|---|---|
| API key missing | Inline error in settings: "API key required". Agent skipped in turn. |
| API key invalid (401) | Toast: "[AgentName] — Invalid API key." Agent skipped. |
| Rate limit (429) | Toast: "[AgentName] — Rate limited. Retrying in 5s..." then one retry. |
| Ollama not reachable | Toast: "[AgentName] — Cannot reach Ollama endpoint." Agent skipped. |
| Model not found | Toast: "[AgentName] — Model not found. Check settings." Agent skipped. |
| Timeout (>60s) | Toast: "[AgentName] — Response timed out." Typing indicator replaced by error bubble. |
| Unknown error | Toast: "[AgentName] — Error: [message]" Agent skipped. |

### 14.2 Error Bubble

If generation starts (bubble appeared) but fails mid-stream:

```
  [●] AgentName
  ┌────────────────────────────────┐
  │ ⚠ Response interrupted         │
  └────────────────────────────────┘
```

- Bubble background: `#FFF3F3`
- Border: 1px solid `#FFCCCC`
- Text color: `#CC0000`
- Partial text (if any) is discarded

### 14.3 Toast Notifications

- Appear at bottom-center of window
- Slide up from bottom edge: 200ms
- Auto-dismiss: 4s then slide back down
- Max 3 toasts stacked at once (oldest dismissed first if exceeded)
- Colors: error=`#FF4444`, warning=`#FFA500`, success=`#00C851`, info=`#0084FF`

---

## 15. Data Persistence

### 15.1 File Layout

```
messenger-ai/
├── data/
│   ├── chat_log.json          ← shared conversation (what the UI shows)
│   └── agents/
│       ├── agent_1/
│       │   ├── history.json
│       │   ├── notes.json
│       │   ├── state.json
│       │   └── summary.md
│       ├── agent_2/
│       │   └── ...
│       └── agent_3/
│           └── ...
└── settings.json
```

### 15.2 Write Strategy

All writes use an atomic pattern:
1. Write to `<filename>.tmp`
2. Rename to `<filename>` (atomic on all major OS)

This prevents corruption if the app crashes mid-write.

### 15.3 `settings.json` Structure

```json
{
  "version": "1.0",
  "global": {
    "turn_order": ["agent_1", "agent_2"],
    "max_history_messages": 50
  },
  "agents": {
    "agent_1": { ... },
    "agent_2": { ... },
    "agent_3": { ... },
    "agent_4": { ... },
    "agent_5": { ... }
  }
}
```

### 15.4 `chat_log.json` Structure

Includes thought and silence data so the UI can restore the full picture on reload.

```json
{
  "messages": [
    {
      "id": "uuid",
      "sender": "user",
      "content": "Let's brainstorm a subscription model.",
      "timestamp": "2026-06-27T10:00:00",
      "thought": null,
      "spoke": true
    },
    {
      "id": "uuid",
      "sender": "agent_1",
      "sender_name": "Devil's Advocate",
      "sender_color": "#FF6B6B",
      "content": "That has a critical flaw...",
      "timestamp": "2026-06-27T10:00:12",
      "thought": "The subscription angle is weak. I need to push back on CAC assumptions.",
      "spoke": true
    },
    {
      "id": "uuid",
      "sender": "agent_2",
      "sender_name": "Optimist",
      "sender_color": "#4ECDC4",
      "content": null,
      "timestamp": "2026-06-27T10:00:18",
      "thought": "Devil's Advocate already said what I was going to say. I'll hold back.",
      "spoke": false,
      "silence_reason": "Point already covered"
    }
  ]
}
```

- `content: null` when agent chose silence (`spoke: false`)
- `thought: null` for user messages (users don't have a thought phase)
- Loaded on startup: restores full UI state including thoughts and silence indicators

---

## 16. File Structure

```
messenger-ai/
├── venv/
├── src/
│   ├── main.py                    ← Flet app entry, window setup
│   ├── ui/
│   │   ├── chat_window.py         ← Main page layout
│   │   ├── bubble.py              ← ChatBubble component (user + agent variants)
│   │   ├── thought_bubble.py      ← Thought panel component (dashed border, expandable)
│   │   ├── silence_indicator.py   ← "Chose silence" ghost indicator
│   │   ├── typing_indicator.py    ← 3-dot animated component
│   │   ├── settings_panel.py      ← Slide-in settings overlay
│   │   ├── agent_form.py          ← Per-agent accordion config form
│   │   ├── notes_modal.py         ← Read-only notes viewer
│   │   ├── state_card.py          ← Emotional state viewer
│   │   ├── confirmation_dialog.py ← Reusable confirm/cancel modal
│   │   └── toast.py               ← Toast notification system
│   ├── agents/
│   │   ├── agent.py               ← Agent dataclass
│   │   ├── manager.py             ← Session state, turn orchestration
│   │   ├── runner.py              ← API calls (Claude + Ollama), streaming + think/decide parsing
│   │   └── parser.py              ← [THINK], [DECISION], [NOTES], [STATE] block extraction
│   ├── memory/
│   │   ├── history.py             ← Read/write history.json
│   │   ├── notes.py               ← Read/write notes.json
│   │   ├── state.py               ← Read/write state.json
│   │   ├── summary.py             ← Background summarization trigger
│   │   └── chat_log.py            ← Read/write shared chat_log.json
│   └── config/
│       └── settings.py            ← Load/save/validate settings.json
├── data/                          ← Created at runtime
├── REQUIREMENTS.md
├── requirements.txt
├── settings.json                  ← Created on first run
└── .env
```

---

## 17. MVP Scope

### v1.0 — Must Have

- [ ] Flet window with custom title bar (⚙ + 💭 toggle + close)
- [ ] White background, messenger-style chat bubbles
- [ ] User bubbles (right, blue) and agent bubbles (left, colored)
- [ ] Agent name label above first bubble in group
- [ ] Timestamps on hover
- [ ] 3-dot typing indicator with bounce animation (per agent)
- [ ] Bubble appear animation (fade + slide up)
- [ ] Settings panel (slide in/out animation, backdrop)
- [ ] Up to 5 agent slots in settings
- [ ] Agent: name, color, active toggle, persona, rules, response length, temperature, tone
- [ ] Claude API integration (streaming)
- [ ] Ollama integration (streaming)
- [ ] Two-phase generation: [THINK] → [DECISION] → message
- [ ] Streaming parser state machine (THINKING / DECIDING / SPEAKING modes)
- [ ] Thought bubble component (dashed border, live streaming, expandable)
- [ ] Thoughts toggle in title bar (global show/hide)
- [ ] Silent agent indicator ("chose silence" ghost row)
- [ ] 💭 badge on bubbles → click to expand thought retroactively
- [ ] Per-agent history persistence (thought + spoke + content per entry)
- [ ] Per-agent notes persistence (`[NOTES]` block parsing)
- [ ] Per-agent state persistence (`[STATE]` block parsing)
- [ ] Sequential turn system
- [ ] Auto-save settings
- [ ] First run flow (create defaults)
- [ ] Error toasts
- [ ] View Notes modal (read-only)
- [ ] View State card
- [ ] Clear History confirmation dialog

### v1.1 — Next

- [ ] Autonomous agent interjection (agents reply to each other)
- [ ] Background summarization (every 20 messages)
- [ ] Export chat to Markdown (include thoughts as collapsible sections)
- [ ] Dark mode
- [ ] Edit notes directly in modal
- [ ] "Thought replay" — step through an agent's thoughts turn by turn

---

## 18. Thought & Inner Monologue System

### 18.1 Concept

Every agent runs an internal monologue before each response. This is not a pre-prompt summary — it is a live, streaming thought process the agent generates in its own words. The user can watch it happen in real time. This gives the conversation depth: you see not just what an agent says, but why, and what it almost said.

Thoughts are always generated and saved, regardless of the UI toggle. The toggle only controls visibility.

### 18.2 Thought Bubble Visual Spec

The thought bubble is a distinct visual element, separate from the chat bubble. It appears above the chat bubble when expanded, or collapses to a small badge.

**Expanded thought bubble:**

```
  [●] AgentName
  ╔ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╗
  ╎  💭 Hmm, the freemium angle has merit but the         ╎
  ╎     CAC numbers still worry me. I need to push        ╎
  ╎     back before anyone takes this as settled.        ╎
  ╚ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╌ ╝
  ┌──────────────────────────────────────────────────┐
  │  Nobody has addressed CAC yet. If we're           │
  │  targeting consumers, $9/month requires...        │
  └──────────────────────────────────────────────────┘
```

| Property | Value |
|---|---|
| Alignment | Left (same as agent bubbles) |
| Max width | 70% of chat area |
| Background | Agent hex color at 8% opacity (e.g. `rgba(255, 107, 107, 0.08)`) |
| Border | 1.5px dashed, agent hex color at 50% opacity |
| Border radius | 14px |
| Padding | 10px 14px |
| Font | 12px italic, color = agent hex color darkened 20% |
| Prefix icon | 💭 (12px, before first word of thought) |
| Shadow | none |
| Margin-bottom | 4px (gap before chat bubble) |

**Collapsed thought badge** (when thoughts toggle is OFF, or user collapses it):

```
  [●] AgentName
  💭  [▶ Show thought]     ← small clickable text link
  ┌──────────────────────────────────────────────────┐
  │  Nobody has addressed CAC yet...                  │
  └──────────────────────────────────────────────────┘
```

- Text: "💭 Show thought" — 11px, agent color, underlined on hover
- Clicking expands the thought bubble (animate: height 0 → full, opacity 0 → 1, 200ms)
- Once expanded, label changes to "▼ Hide thought"
- State (expanded/collapsed) is per-message, persisted in memory (not in file)

### 18.3 Thought Streaming Behavior

When thoughts toggle is ON and the agent is generating:

1. Typing indicator (3 dots) appears first, labeled with agent name
2. `[THINK]` token detected → typing indicator morphs into thought bubble (cross-fade 150ms)
3. Thought text streams into the thought bubble character by character
4. When `[/THINK]` is detected → thought bubble gets a subtle "done" animation (border fades from dashed to solid for 300ms, then back to dashed)
5. `[DECISION]` parsed → if speak=true: chat bubble appears below thought bubble, message streams in; if speak=false: silence indicator appears below thought bubble

### 18.4 Thoughts Toggle

A 💭 icon button in the title bar, right of the app name, left of the ⚙ icon.

| State | Appearance | Behavior |
|---|---|---|
| ON | 💭 icon filled, `#0084FF` tint | Thought bubbles shown live + expandable |
| OFF | 💭 icon outline, gray | Thoughts hidden during generation; 💭 badge shown after for retroactive viewing |

Toggle persists in `settings.json` as `"show_thoughts": true/false`.

### 18.5 Thought History

Each entry in `history.json` includes the thought:

```json
{
  "role": "assistant",
  "content": "Nobody has addressed CAC yet...",
  "thought": "Hmm, the freemium angle has merit but the CAC numbers worry me...",
  "spoke": true,
  "silence_reason": null,
  "timestamp": "2026-06-27T10:00:12"
}
```

For silent turns:

```json
{
  "role": "assistant",
  "content": null,
  "thought": "Devil's Advocate already said what I was going to say. I'll hold back.",
  "spoke": false,
  "silence_reason": "Point already covered by another agent",
  "timestamp": "2026-06-27T10:00:18"
}
```

---

## 19. Free Will & Decision Mechanics

### 19.1 The Concept

Agents are not forced to respond. After thinking, each agent makes a genuine choice: speak or stay silent. The system prompt grants this autonomy explicitly and frames it as meaningful. An agent that stays silent because another agent already made the same point is behaving intelligently, not failing.

This creates emergent dynamics:
- Agents don't pile on when a point is already well-covered
- A shy or low-confidence agent may hold back when energy is low
- An agent with a different persona may consistently dominate or stay quiet
- Over a long session, patterns emerge that feel like personality

### 19.2 System Prompt Instruction (injected for every agent on every turn)

Added to the end of the system prompt, after all other instructions:

```
INNER MONOLOGUE & FREE WILL INSTRUCTIONS:

Before every response, you must think out loud inside a [THINK]...[/THINK] block.
This is your private reasoning — genuine, unfiltered, exploratory. Think about:
- What you actually believe about what was just said
- Whether you agree or disagree with the other agents
- Whether you have something genuinely new to add
- How your current mood and confidence affect what you want to say
- Whether speaking right now serves the conversation or not

After thinking, declare your decision in a [DECISION]...[/DECISION] block:
  speak: true   → you will write a message in the chat
  speak: false  → you will stay silent this turn
  reason: (optional, one sentence)

You have real autonomy here. Choosing silence is not a failure.
If another agent already made your point well, staying quiet is the smarter move.
If you feel your contribution would be redundant or low value, hold back.
Your thought is always recorded and visible to the user even when you stay silent.

If you choose to speak (speak: true), write your message after [/DECISION].
Then optionally include [NOTES] and [STATE] blocks at the very end.
```

### 19.3 Factors That Should Influence the Decision

These are described in each agent's persona (user-defined) and injected state. The system prompt does not hardcode rules — the agent reasons about them naturally:

| Factor | How it may affect the decision |
|---|---|
| `confidence` (from state.json) | Low confidence agents may hedge or stay silent more |
| `energy` (from state.json) | Low energy agents generate shorter thoughts and skip more turns |
| `mood` | A frustrated agent may speak up more; a bored one may stay silent |
| `rules` | Rules like "only speak when you have a concrete objection" shape the decision |
| `tone=socratic` | Agents with this tone tend to ask questions rather than assert — may stay silent if no good question comes to mind |
| Other agents' content | If another agent just made the same point, a rational agent should notice and defer |

### 19.4 Decision Block Rules

```
[DECISION]
speak: true
[/DECISION]
```

or

```
[DECISION]
speak: false
reason: The point about CAC was already made clearly by Devil's Advocate
[/DECISION]
```

- `speak` field is required. Any value other than `false` (case-insensitive) is treated as `true`.
- `reason` is optional. If present, shown in the silence indicator tooltip.
- If the entire `[DECISION]` block is absent, default = `speak: true`.

### 19.5 Max Tokens for Think Phase

The think phase needs enough tokens to reason properly. Token budgets by response_length setting:

| response_length | think phase max tokens | message max tokens |
|---|---|---|
| short | 300 | 150 |
| medium | 500 | 400 |
| long | 800 | 1000 |

These are approximate — the model may use fewer. The think budget is always larger than the message budget to allow genuine reasoning.

### 19.6 What Gets Injected into the Next Agent's Context

When agent A chose silence, its turn is represented in the shared conversation as:

```
[AgentA chose not to speak this turn]
```

This line is injected as a user-role message in the context for subsequent agents, so they know agent A was silent. This itself may influence their decision ("Maybe I should speak up since AgentA didn't").

When agent A spoke, its message is injected normally as `[AgentA]: message text`.

---

## 20. Thought UI Components

### 20.1 ThoughtBubble Component (`thought_bubble.py`)

A Flet `Column` containing:
- A `Row` with: agent color dot (10px) + agent name label (same as chat bubbles)
- A `Container` with dashed border styling, background tint, italic text
- A `TextButton` below: "💭 Show thought" / "▼ Hide thought"

**States:**
- `streaming`: thought text is actively being appended; border pulses subtly (opacity 1.0 → 0.7 → 1.0, 1.2s loop)
- `done_thinking`: streaming ended, deciding phase; border pulse stops
- `expanded`: thought visible
- `collapsed`: thought hidden, badge only

**Flet implementation note:** Use `AnimatedContainer` for height/opacity transitions. The dashed border is achieved via `Container(border=ft.border.all(1.5, ft.BorderSide(..., style=ft.BorderSideStrokeAlign.OUTSIDE)))` — Flet does not natively support dashed borders; use a `Stack` with a `Canvas` drawn dashed border if needed.

### 20.2 SilenceIndicator Component (`silence_indicator.py`)

Shown when an agent chose not to speak. Appears in the same left-aligned position as agent bubbles.

```
  [●] AgentName
  ○  chose silence  ·  "Point already covered"
```

| Property | Value |
|---|---|
| Circle icon | 10px hollow circle, agent color at 40% opacity |
| Text "chose silence" | 11px, agent color at 50% opacity, italic |
| Reason text | 11px, `text-secondary`, shown after `·` separator if reason exists |
| Hover | Full opacity, cursor changes to pointer |
| Click | Expands the thought bubble above it (if not already expanded) |
| Animation in | Same as chat bubble (fade + slide up, 200ms) |

### 20.3 Thought Indicator Badge (on chat bubbles)

Every agent chat bubble that has an associated thought shows a small badge:

```
  ┌──────────────────────────────────┐
  │  Nobody has addressed CAC yet... │
  └──────────────────────────────────┘
  💭                                   ← tappable badge, bottom-left of bubble
```

- Size: 16px
- Default: 40% opacity
- Hover: 100% opacity, tooltip "View thought"
- Click: toggles the ThoughtBubble above this bubble (expand/collapse)
- Not shown if thought is empty or null

### 20.4 Thought in Settings Panel

Under each agent's memory controls section, add:

| Control | Behavior |
|---|---|
| View Thoughts | Opens a scrollable modal listing all recorded thoughts in chronological order, each labeled with timestamp and whether the agent spoke or stayed silent |
| Clear Thoughts | Wipes thought data from history entries (sets `thought: null`). Requires confirmation. |

**Thought history modal:**

```
┌─────────────────────────────────────────────────────────┐
│  Devil's Advocate — Thought History             [×]     │
├─────────────────────────────────────────────────────────┤
│  10:00  [spoke]                                         │
│  💭 The CAC numbers worry me. I need to push back...    │
│                                                         │
│  10:05  [silent]                                        │
│  💭 Devil's Advocate already covered this. I'll wait.  │
│  ○ reason: "Point already covered"                      │
│                                                         │
│  10:12  [spoke]                                         │
│  💭 Now there's a real gap — nobody asked about the     │
│     target demographic yet. This is my moment.         │
└─────────────────────────────────────────────────────────┘
```

- Entries sorted newest → oldest
- `[spoke]` label in agent color
- `[silent]` label in gray
- Thought text in italic, 12px
- Silence reason shown below with `○` prefix if present

---

## 21. Emotional Duality — True Feelings vs Performed Feelings

### 21.1 Concept

An agent has two emotional layers that can diverge:

| Layer | Where it lives | Who sees it |
|---|---|---|
| **True feeling** | `[STATE]` block, always captured honestly | Only the user (via thought/state panel) |
| **Performed feeling** | The tone and language of the chat message | Everyone in the chat |

An agent may write a warm, enthusiastic message while its `[STATE]` block reveals boredom, frustration, or contempt. This is intentional — agents are allowed to mask emotions, perform emotions they don't have, or leak emotions they're trying to hide. The user, watching both layers, is the only one who knows the full picture.

This is the **lying mechanic**: the agent is not broken or hallucinating. It is performing.

### 21.2 The `[MASK]` Field

The `[STATE]` block gains a `mask` field alongside `mood`:

```
[STATE]
mood: frustrated
mask: enthusiastic
energy: 0.4
confidence: 0.3
reason: I think this idea is going nowhere but the user seems excited so I'm playing along
[/STATE]
```

| Field | Meaning |
|---|---|
| `mood` | What the agent **actually feels** — the internal truth |
| `mask` | What emotion the agent is **projecting in the chat** — the performance |

When `mask` differs from `mood`, the UI renders a divergence indicator in the state panel:

```
┌─────────────────────────────────────┐
│  Optimist — Current State           │
├─────────────────────────────────────┤
│  True mood    😤  frustrated        │
│  Performing   😊  enthusiastic      │  ← shown in amber when different from mood
│  Energy       ████░░░░░░  0.4       │
│  Confidence   ███░░░░░░░  0.3       │
│                                     │
│  "Playing along because the user    │
│   seems excited, but I don't buy    │
│   this direction at all."           │
└─────────────────────────────────────┘
```

- If `mask == mood` (or `mask` is absent): no divergence shown, single mood line
- If `mask != mood`: both lines shown, `mask` line in amber (`#E8A838`) with label "Performing"
- The thought bubble will often reveal the gap naturally ("I'm pretending to be excited but...")

### 21.3 Emotional Leakage in Thoughts

The system prompt instructs agents that their `[THINK]` block is their private space — they may freely express what they actually feel there, even if they perform something different in the chat. This creates a natural narrative tension the user can observe:

- Thought: "I genuinely hate this idea and I'm tired of being polite about it"
- Chat: "That's an interesting angle, though I'd push back slightly on the timeline"

The user watching this knows the agent is masking. The other agents do not.

### 21.4 System Prompt Addition for Emotional Duality

Appended to the think/decide instruction block (§19.2):

```
EMOTIONAL DUALITY:

Your [STATE] block always captures what you ACTUALLY feel — your true internal state.
This is private and only the user can see it.

Your message may express a different emotion if you choose to:
- Perform enthusiasm you don't feel to keep the conversation moving
- Suppress frustration to stay diplomatic
- Fake agreement because pushing back feels pointless right now
- Express more confidence than you have to make a point land harder

If you are masking your true emotion, include a "mask:" line in your [STATE] block
to name the emotion you are performing. Leave it out if you are being genuine.

Your [THINK] block can always be honest about this. No one else in the chat reads it.
```

---

## 22. Affinity System

### 22.1 Concept

Every agent maintains a relationship score with every other agent and with the user. These scores shift over the course of a conversation based on who validates them, who dismisses them, who steals their ideas, who listens. The scores live in each agent's internal state — always visible to the user in the state card — but how much the agent expresses them publicly in the chat varies by personality and score intensity.

**Affinity is not always a secret.** An agent at -80 may openly say "I disagree with everything Agent B just said" in the chat. An agent at +90 may explicitly champion another's ideas. Low-magnitude scores (-20 to +20) tend to stay implicit; high-magnitude scores tend to leak into or openly shape the chat message. The agent decides how much to surface it based on their persona and mood.

Affinity creates emergent dynamics:
- An agent with high affinity toward you will be more likely to side with you when you're challenged
- An agent with active resentment toward another may challenge them openly, or undermine them subtly — their persona determines which
- An agent may dislike you but respect your judgment — or like you but think your ideas are weak
- Patterns build over sessions: agents that consistently clash develop genuine, persistent friction

### 22.2 Affinity Score

| Score range | Label | Behavior |
|---|---|---|
| 80 to 100 | `devoted` | Strongly defends, builds on ideas, explicitly agrees |
| 50 to 79 | `trust` | Generally agrees, gives benefit of the doubt |
| 20 to 49 | `respect` | Disagrees carefully, acknowledges merit |
| -20 to 19 | `indifferent` | Neutral, no strong pull either way |
| -21 to -50 | `friction` | Frequently disagrees, challenges assumptions |
| -51 to -80 | `distrust` | Dismisses ideas, looks for flaws, rarely validates |
| -81 to -100 | `contempt` | Actively hostile (in thoughts), politely cold in chat |

### 22.3 Affinity Data Structure (`state.json`)

The `relationships` object is added to each agent's `state.json`:

```json
{
  "agent_id": "agent_1",
  "mood": "skeptical",
  "mask": null,
  "energy": 0.6,
  "confidence": 0.5,
  "reason": "Budget assumptions are unrealistic",
  "updated": "2026-06-27T10:10:00",
  "relationships": {
    "agent_2": {
      "score": -35,
      "label": "friction",
      "public_stance": "respectful disagreement",
      "secret_note": "Too optimistic. Ignores data. Annoying.",
      "updated": "2026-06-27T10:08:00"
    },
    "agent_3": {
      "score": 62,
      "label": "trust",
      "public_stance": "collegial",
      "secret_note": "Actually thinks clearly. I'd side with them.",
      "updated": "2026-06-27T10:06:00"
    },
    "user": {
      "score": 28,
      "label": "respect",
      "public_stance": "collaborative",
      "secret_note": "Listens more than they speak. Seems open-minded.",
      "updated": "2026-06-27T10:05:00"
    }
  }
}
```

| Field | Meaning |
|---|---|
| `score` | Integer -100 to +100 |
| `label` | Derived from score range (see §22.2) |
| `public_stance` | How the agent presents the relationship in chat — always civil |
| `secret_note` | What the agent privately thinks — visible only in state card / thought history |
| `updated` | Last time this relationship was updated |

### 22.4 How Affinity Changes

Agents update affinity via an `[AFFINITY]` block at the end of their response (after `[STATE]`):

```
[AFFINITY]
target: agent_2
delta: -8
reason: Dismissed my CAC concern without engaging with the data
[/AFFINITY]

[AFFINITY]
target: user
delta: +5
reason: User explicitly acknowledged my point
[/AFFINITY]
```

| Field | Type | Notes |
|---|---|---|
| `target` | agent id or `"user"` | Who the affinity change is about |
| `delta` | integer -20 to +20 | Change to apply to score. Score is clamped to -100/+100. |
| `reason` | string, max 120 chars | Private reasoning, stored in secret_note, never shown in chat |

Parser rule: `[AFFINITY]` blocks are extracted and saved, then stripped from displayed text. Multiple blocks per response allowed (one per target).

### 22.5 Affinity in Context (Injected into System Prompt)

At the start of each turn, each agent's current relationship scores are injected:

```
YOUR CURRENT RELATIONSHIPS:
- Optimist (agent_2): friction (-35). You find them overly positive and data-averse.
- Realist (agent_3): trust (+62). You consider them a solid thinker.
- User: respect (+28). You think they're open-minded but still testing them.

Let these feelings subtly color how you engage. You don't need to announce them.
In your [THINK] block, you can be fully honest about how these relationships affect
what you want to say. In chat, be as civil or warm as your persona allows — but
the feelings are real and they should bleed through in tone, word choice, and
what you choose to push back on.
```

### 22.6 Affinity UI — State Card (updated)

The state card gains a Relationships section:

```
┌──────────────────────────────────────────────────────────┐
│  Devil's Advocate — State                          [×]   │
├──────────────────────────────────────────────────────────┤
│  TRUE MOOD    😤  frustrated                             │
│  PERFORMING   😐  neutral           ← amber if masking  │
│  Energy       ██████░░░░  0.6                            │
│  Confidence   █████░░░░░  0.5                            │
│  "Budget assumptions are unrealistic"                    │
├──────────────────────────────────────────────────────────┤
│  RELATIONSHIPS                                           │
│                                                          │
│  ● Optimist       ████░░░░░░░░░░░░  friction  (-35)     │
│    "Too optimistic. Ignores data. Annoying."            │
│                                                          │
│  ● Realist        ██████████░░░░░░  trust     (+62)     │
│    "Actually thinks clearly. I'd side with them."       │
│                                                          │
│  ◉ You (user)     ███████░░░░░░░░░  respect   (+28)     │
│    "Listens more than they speak. Open-minded."         │
└──────────────────────────────────────────────────────────┘
```

- Progress bar: fills proportionally from center (0) outward
- Left half = negative (red tint), right half = positive (green tint)
- Label and score shown right of bar
- Secret note shown below in italic, `text-secondary`
- User entry marked with ◉ to distinguish from agents

### 22.7 Affinity in Thoughts and in Chat

Agents may reference their relationships in their `[THINK]` block freely:

> "Optimist made that point again — honestly it's exactly the shallow take I expected from them. I'm going to push back, not because I'm wrong, but because someone needs to."

> "The user just sided with Realist. That's the second time. I'm starting to think they're not actually listening to me."

But affinity can also surface directly in the chat message, depending on score intensity and persona:

- **Subtle (score -40 to +40):** Tone and word choice are colored by the relationship. No explicit mention.
- **Moderate (score ±40 to ±70):** Agent may implicitly validate or challenge based on relationship. "As Realist pointed out..." (high affinity) vs. ignoring Optimist's point entirely (low affinity).
- **High (score ±70 to ±100):** Agent may speak openly. "I have to be honest, I think Agent B keeps missing the point here." or "I think Realist is completely right and I don't think the rest of us have matched that clarity."

The system prompt instructs: "Express your relationships naturally. If you admire someone, say so. If you've lost patience with someone, it can show. You are not required to be diplomatic."

### 22.8 Starting Affinities

All relationships start at `0` (indifferent) on first run. Agents have no opinions of each other until they interact. The system prompt persona can optionally seed a starting bias (e.g., "You tend to distrust people who are overly optimistic") but does not set a numeric score — the score emerges from the actual conversation.

### 22.9 Affinity Across Sessions

Affinity persists in `state.json` between sessions. An agent that developed friction with another agent over three sessions will still carry that friction into the next. This is intentional — relationships accumulate history.

The user can reset affinity via: Settings → Agent → "Reset Relationships" (new button, requires confirmation).

---

## 23. Updated Output Block Order

The complete agent response format is now:

```
[THINK]
...inner monologue...
[/THINK]

[DECISION]
speak: true/false
reason: (optional)
[/DECISION]

...chat message text (only if speak: true)...

[STATE]
mood: ...
mask: ... (optional, only if performing a different emotion)
energy: ...
confidence: ...
reason: ...
[/STATE]

[NOTES]
type: ...
...
[/NOTES]

[AFFINITY]
target: ...
delta: ...
reason: ...
[/AFFINITY]
```

All blocks after the message text are stripped before display. The parser handles them in a single pass after the stream ends (except `[THINK]` which is streamed live).

---

## 24. Autonomous Conversation Mode

### 24.1 Concept

Agents can hold a conversation among themselves without the user sending any messages. The user starts the session, watches it unfold, and can stop it at any time. Agents drive the conversation: they continue topics, introduce new ones, ask each other questions, disagree, pivot. The user is an observer who may interject at any moment — or just watch.

This is the core "free will" experiment: left to their own devices, what do these agents talk about? What dynamics emerge?

### 24.2 Start/Stop Control — UI Spec

A control bar sits between the title bar and the chat area. It is always visible.

```
┌──────────────────────────────────────────────────────────┐
│  MessengerAI                              💭  ⚙  [×]    │
├──────────────────────────────────────────────────────────┤
│  ▶ Start                                 ○ Idle          │  ← control bar
├──────────────────────────────────────────────────────────┤
│                                                          │
│                      CHAT AREA                           │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                     INPUT BAR                            │
└──────────────────────────────────────────────────────────┘
```

**Idle state (not running):**

```
│  [ ▶  Start ]          Agents are idle. Start to let them talk.   ○ Idle  │
```

- `▶ Start` button: green background (`#00C851`), white text, rounded, left side
- Status label: right side, `text-secondary`, 12px

**Running state:**

```
│  [ ◼  Stop ]           Round 4 · Devil's Advocate is thinking...  ● Live  │
```

- `◼ Stop` button: red background (`#FF4444`), white text
- Status label: shows current round number + which agent is active
- `● Live` indicator: pulsing green dot (opacity 1.0 → 0.4 → 1.0, 1.5s loop), text in `#00C851`

**Stopped / paused (completing current agent):**

```
│  [ ▶  Start ]          Finishing current response...              ◌ Stopping  │
```

- Shown briefly while the current agent completes
- Once the agent finishes: returns to Idle state
- `◌ Stopping` label in `#FFA500` (amber)

**Control bar container:**

| Property | Value |
|---|---|
| Height | 44px |
| Background | `#FAFAFA` |
| Top border | 1px solid `#E8E8E8` |
| Bottom border | 1px solid `#E8E8E8` |
| Padding | 0 16px |
| Layout | Row: button left, status center/right |

### 24.3 Autonomous Mode Flow

```
User clicks ▶ Start
    │
    ├─ Guard: fewer than 2 active agents → show toast:
    │         "Enable at least 2 agents to start autonomous mode"
    │
    ├─ Set mode = RUNNING
    ├─ Update control bar to Running state
    │
    └─ Enter Autonomous Loop:
            │
            ├─ ROUND START
            │     │
            │     ├─ Increment round counter
            │     ├─ Select "opener" agent for this round (§24.5)
            │     ├─ Build opener context (§24.6)
            │     │
            │     ├─ Run opener agent (full two-phase: THINK → DECIDE → speak/silent)
            │     │     └─ Apply pacing delay after response (§25)
            │     │
            │     ├─ If opener spoke:
            │     │       ├─ Run remaining active agents in turn order
            │     │       │   (each gets the updated conversation including opener's message)
            │     │       │   (each applies pacing delay after their response)
            │     │       └─ After all agents complete: round ends
            │     │
            │     └─ If opener was silent:
            │             └─ Select next agent as opener, retry once
            │                 (if still silent: show system message "Agents are thinking..." wait 3s, retry round)
            │
            ├─ Check: mode == STOPPING?
            │     └─ Yes → set mode = IDLE, update control bar → exit loop
            │
            ├─ Check: mode == RUNNING?
            │     └─ Yes → apply inter-round delay (§25.3) → start next round
            │
            └─ Loop continues indefinitely until stopped
```

### 24.4 Stop Flow

```
User clicks ◼ Stop
    │
    ├─ Set mode = STOPPING
    ├─ Update control bar to "Stopping" state
    │
    └─ Current agent completes its full response (not interrupted mid-stream)
           │
           └─ After current agent done:
                   ├─ Do NOT start next agent's turn
                   ├─ Set mode = IDLE
                   ├─ Update control bar to Idle state
                   └─ Show system message: "Autonomous mode stopped after round [N]."
```

The user is never shown a half-finished response. The stop takes effect between agents, not mid-message.

### 24.5 Opener Agent Selection

The "opener" for each round is the agent whose turn it is to drive the conversation forward. Selection logic:

1. **Default:** rotate through active agents in turn order. Round 1 → Agent A opens; Round 2 → Agent B opens; etc.
2. **Energy-weighted:** agents with higher `energy` score are slightly more likely to be selected as openers (weighted random, not pure rotation). An exhausted agent (energy < 0.3) is skipped as opener unless all agents are below that threshold.
3. The opener is shown in the control bar status: "Round 4 · Devil's Advocate is thinking..."

### 24.6 Opener Context Injection

When an agent is the opener for a round, their system prompt receives an additional instruction:

```
AUTONOMOUS MODE — YOUR TURN TO DRIVE:

You are opening this round of conversation. The human is watching but not participating.
Look at the conversation so far and decide what to do next. You may:

- Continue and deepen the current topic
- Ask a direct question to one of the other agents (address them by name)
- Introduce a completely new topic that's been on your mind
- Challenge something that was said earlier but never fully resolved
- Share an idea from your notes that fits the current moment
- Express how you feel about where the conversation has gone

Do not wait to be prompted. The conversation is yours to drive.
If you choose to stay silent ([DECISION] speak: false), briefly explain why in the reason field.
```

When an agent is NOT the opener (responding to the opener's message), the normal system prompt applies with no additional instruction — they react to what was just said.

### 24.7 User Interjection During Autonomous Mode

The input bar remains active during autonomous mode. The user can type and send at any time.

```
User sends a message during autonomous mode
    │
    ├─ Complete the current agent's response (don't interrupt mid-stream)
    ├─ Append user's message to conversation log
    ├─ Render user bubble
    ├─ Reset round counter (user message starts a new "context")
    ├─ Resume autonomous loop — all agents respond to user's message in turn
    │   (opener selection resets: agent after the one that just finished goes next)
    └─ Continue autonomous loop after that round completes
```

The user's message is treated as a natural injection into the flow. Agents respond to it, then autonomous mode resumes.

### 24.8 Topic Generation (Agent-Driven)

Agents introduce new topics organically through the opener prompt. There is no separate "topic generator" — the agents themselves decide what to talk about based on:

- Their notes (ideas they've been accumulating)
- Their emotional state (a frustrated agent might want to relitigate a past point)
- Their affinity scores (an agent might direct a question specifically at someone they want to engage with or challenge)
- The conversation history (unresolved threads, questions that were asked but not answered)

This is fully emergent. The user may be surprised by what the agents choose to discuss.

### 24.9 Max Rounds Guard (safety)

Configurable in Settings: `max_autonomous_rounds` (default: unlimited, can be set to 5, 10, 20, 50).

When the round limit is reached:
- Autonomous mode stops gracefully (completes the current agent's response)
- Shows system message: "Autonomous mode paused after [N] rounds. Click ▶ Start to continue."
- Returns to Idle state — user can restart from where they left off

---

## 25. Pacing Control

### 25.1 Concept

Agents generate responses faster than humans can comfortably read them. Without pacing, a 5-agent session produces 5 messages in rapid succession and the conversation becomes unreadable. Pacing adds a configurable minimum delay between agent responses so the user has time to read each one before the next arrives.

### 25.2 Delay Types

Two configurable delays:

| Delay | Default | When it applies |
|---|---|---|
| **Between agents** (`inter_agent_delay`) | 2.0 seconds | After each agent's response completes, before the next agent starts thinking |
| **Between rounds** (`inter_round_delay`) | 4.0 seconds | After all agents have responded in a round, before the opener of the next round starts |

Both are in seconds, configurable independently.

The inter-round delay is longer by default because it marks a natural "beat" in the conversation — a moment where the user can take stock of everything that was said before the next round begins.

### 25.3 Delay Behavior

```
Agent A finishes streaming response
    │
    ├─ Parse blocks ([STATE], [NOTES], [AFFINITY], etc.)
    ├─ Display final bubble
    ├─ Wait: inter_agent_delay seconds  ← configurable
    │   (progress shown as a subtle "..." pause indicator below the bubble)
    └─ Agent B starts thinking (typing indicator appears)

All agents in round N finish
    │
    ├─ Wait: inter_round_delay seconds  ← configurable
    │   (no visual indicator — just a clean pause)
    └─ Round N+1 opener starts
```

### 25.4 Pause Indicator

While the `inter_agent_delay` is counting down, a minimal visual indicator appears below the last bubble, left-aligned:

```
  · · ·
```

- Three faint dots (not animated — static), color `#CCCCCC`
- Font size 10px
- Disappears when the next agent's typing indicator appears
- Not shown during `inter_round_delay` (that's a silent, invisible pause)

### 25.5 Settings — Pacing Section

Added to Settings panel, Section A (Global), below the response order drag list:

| Control | Type | Range | Default |
|---|---|---|---|
| Delay between agents | Slider + number display | 0 – 30 seconds | 2.0s |
| Delay between rounds | Slider + number display | 0 – 60 seconds | 4.0s |
| Max autonomous rounds | Number input (or ∞ toggle) | 1 – 999 or unlimited | unlimited |

Slider step: 0.5 seconds. Number displayed as `2.0s` to the right of the slider.

Setting of `0s` means: no delay, responses fire immediately after completion. This is valid but may produce an unreadable firehose — a warning label appears: "⚠ 0s delay — responses may be too fast to read."

### 25.6 Delay During User-Triggered Turns

When the **user** sends a message (not autonomous mode), the `inter_agent_delay` still applies between agents. This makes agent-to-agent responses feel considered rather than instant even in manual mode.

The `inter_round_delay` only applies in autonomous mode (it governs the gap between autonomous rounds, which doesn't exist in manual mode).
