# Braille Onboarding Plan

## First-boot behavior
1. Detect Braille device (USB/BT) during service startup.
2. Emit `caps.report` with `braille_adapter` presence so orchestrator/renderer can branch into Braille-first flow.
3. Send tactile greeting: e.g., write “UnisonOS Braille ready.” to display.
4. Offer Braille-only menu:
   - Set language / Braille table (UEB Grade 1/2 initially).
   - Choose 6 vs 8 dots.
   - Confirm pairing/keep alive.

## Input mapping for onboarding
- Standard Braille keys map to navigation:
  - Space+Dot1: Up, Space+Dot4: Down, Space+Dot3: Left, Space+Dot6: Right.
  - Space+Dots1-4: Select/Enter.
  - Space+Dots1-5: Back.
- Routing keys move cursor/focus across menu items.
- Text entry uses selected table; echo to display.

## Output rendering
- Minimal menu strings translated via `BrailleTranslator` into cells.
- Support panning (left/right) to view longer strings; maintain logical cursor position.
- Cursor routing keys should request focus move to item under the key (integration with renderer focus API).

## Flow outline
1. Greeting.
2. Language selection (cycle through options with nav keys; confirm).
3. Braille table selection (UEB Grade 1/2; future tables configurable).
4. Dot-count selection (6 vs 8).
5. Confirmation message and handoff to main UI; continue mirroring focus text.

## Dependencies / assumptions
- Renderer or onboarding service exposes a focus/text feed the Braille adapter can subscribe to (WS or poll).
- Policy allows Braille output without prior consent for onboarding (or a minimal local-only policy gate).
- Device driver supports basic display write + key events.
