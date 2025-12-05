# Braille Architecture Plan

## Goals
- Modular, transport-agnostic Braille I/O service with plug-in drivers and translation tables.
- First-class modality: detect devices at boot, emit `caps.report`, and enable Braille-only onboarding.
- Clean mapping between Braille events and existing Unison input/output schemas.

## Core modules
- **BrailleDeviceManager**
  - Discovers devices (USB HID, Bluetooth HID; later serial/custom).
  - Maintains registry and lifecycle (attach/detach, reconnect).
  - Chooses a `BrailleDeviceDriver` based on VID/PID/Bluetooth descriptors.
- **BrailleDeviceDriver (interface)**
  - Responsibilities:
    - Low-level framing/parsing of vendor protocol.
    - Emit normalized events: key chords, routing keys, nav keys, status keys.
    - Accept display updates: braille cell matrix, cursor position, panning.
  - API shape (Python sketch):
    ```python
    class BrailleDeviceDriver(Protocol):
        def open(self, device_info): ...
        def close(self): ...
        def send_cells(self, cells: BrailleCells): ...
        def on_packet(self, data: bytes) -> Iterable[BrailleEvent]: ...
    ```
- **BrailleTranslator**
  - Pluggable tables (UEB Grade 1/2, 6/8-dot; future language tables).
  - APIs: `text_to_cells(text, config)` and `cells_to_text(cells, config)`.
  - Configurable per person/session via context service (similar to BCI decoder prefs).
- **BrailleIOAdapter**
  - Bridges device events to Unison envelopes and vice versa.
  - Input: Braille key/chord → `input.command`/`input.text` envelopes; optional HID mapping.
  - Output: subscribes to focus/selection text (renderer/onboarding) → translate → push to device; handles panning/cursor routing.
- **BrailleOnboardingHelper**
  - Braille-only greeting, language/table selection, 6/8-dot choice.
  - Minimal menu tree navigable via standard Braille keys.
- **Driver registry**
  - `BrailleDeviceDriverRegistry` mapping device IDs to driver classes; defaults to a generic HID driver for standard Braille HID usage.

## Data models
- **BrailleCells**: `rows x cols` grid; each cell has 6 or 8 dot boolean states; includes cursor position metadata.
- **BrailleEvent**: `{type: "chord"|"routing"|"nav"|"status", keys: [...], timestamp, device_id}`.
- **DeviceInfo**: `{id, transport: usb|bt|serial, vid, pid, name, capabilities: {cells, routing_keys, keyboard_layout}}`.

## Internal event schema (aligned with EventEnvelope)
- `event_type`: `braille.input` (or mapped to `input.command`/`input.text`).
- `payload.intent` for nav commands, `payload.text` for text entry.
- `auth_scope`: `braille.input.read`; device attach uses `braille.device.pair`.
- Output path uses device manager API; diagnostics via `WS /braille/raw` (mirrors packets/cell buffers).

## Security/consent
- Service enforces Braille scopes similar to BCI scopes:
  - `braille.input.read`, `braille.output.write`, `braille.device.pair`, `braille.profile.manage`.
- Device access occurs in the Braille service container; host must allow USB/Bluetooth passthrough per deployment.

## Transport strategy
- **USB**: libusb/hidapi enumeration; match VID/PID to driver registry.
- **Bluetooth**: use Bleak/BlueZ HID profile; match descriptors to drivers.
- **Serial (later)**: opt-in driver to parse vendor serial protocols.

## Driver plugin model
- Registry keyed by device identifiers:
  ```python
  DRIVER_REGISTRY = {
      ("0x1c71", "0xc007"): HumanWareDriver,
      ("bt", "focus40"): FreedomScientificBTDriver,
  }
  ```
- Adding a driver: implement interface, register in `drivers/registry.py`, add unit tests + sample packet fixtures.

## Output rendering pipeline
1. Subscribe to focus/selection updates (proposed `/focus/stream` or similar from renderer).
2. Translate text → Braille cells via `BrailleTranslator`.
3. Send to active device(s) via `BrailleDeviceManager`.
4. Handle panning/cursor routing events to request more text or move focus.

## Onboarding hooks
- On device detection at boot:
  - Emit `caps.report` with `braille_adapter`.
  - Send tactile greeting on display.
  - Offer Braille-only onboarding (language/table/6-8-dot).
- Uses `BrailleOnboardingHelper` and minimal text prompts translated to Braille.

## Testing & simulation
- Simulated driver feeds canned packets and accepts cell writes; used in unit tests and CI.
- Translator tests cover multiple tables/configs.
- Manager tests mock device enumeration and driver selection.

## Open questions / blockers
- Need a stable focus/text feed from renderer/shell for Braille output; propose adding a small WS/poll endpoint.
- Consent/policy scopes for Braille not yet codified; mirror BCI pattern.
- Final decision on transport libraries (hidapi/libusb, Bleak); pick based on devstack base image compatibility.
