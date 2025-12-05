# Braille I/O Integration Overview

## Existing I/O patterns in UnisonOS
- **Event schema**: `unison-docs/dev/specs/schemas/event-envelope.md` defines the envelope used by all modalities (`event_type` like `bci.intent`, `caps.report`, `input.*`). Braille should emit:
  - `caps.report` on startup: `{braille_adapter: {present: true, model, transport, cells, input_keys}}`.
  - Input as either `input.command`/`input.text` events (or a Braille-specific `braille.input` if needed for richer metadata) consumed by `unison-intent-graph` and orchestrator.
  - HID-like key events when mapped (similar to `input.hid` used by `unison-io-bci`).
- **Input ingress**: Other IO services (e.g., `unison-io-bci`, `unison-io-speech`, `unison-io-core`) post events to orchestrator (`/event`) or intent-graph using the envelope. WebSockets are used for diagnostics/raw mirrors.
- **Output/focus**: `unison-experience-renderer` + shell receive focus/selection changes; Braille display output should subscribe to focus/selection text or a new lightweight `/braille/output` channel. If not available, fall back to mirroring current UI text via orchestrator/intent-graph notifications.
- **Onboarding**: Startup modality docs (`unison-docs/dev/startup-modality.md`) describe `caps.report` gating prompts. Braille onboarding should plug into that: if `braille_adapter.present` emit, the renderer/onboarding can switch to Braille-first flows.
- **Auth/policy/consent**: Similar to BCI, expect scopes for device access/config:
  - `braille.device.pair`, `braille.input.read`, `braille.output.write`, `braille.profile.manage`.
  - Enforce via JWT/consent middleware in the service (see `unison-io-bci/src/auth.py` pattern).

## Integration touchpoints
- **Input path**: Braille key/chord/routing events → normalize to Unison input schema → POST to orchestrator `/event` (or intent-graph) with `auth_scope` set (e.g., `braille.input.read`). Provide optional HID mapping for legacy paths.
- **Output path**: Subscribe to focus/selection updates (TBD: renderer hook) and render via BrailleTranslator to device buffers. Provide WebSocket `/braille/output` for debugging and mirroring.
- **Device discovery**:
  - USB: enumerate HID and known vendor VID/PIDs; map to `BrailleDeviceDriver`.
  - Bluetooth: similar HID matching; allow vendor-specific pairing hooks.
- **Onboarding**: When a Braille device is detected at boot, send a tactile greeting and present a minimal Braille-only menu (language, table, 6/8-dot) before any visual/audio dependency.

## Gaps/assumptions
- No existing Braille service; we will model the service after `unison-io-bci` (FastAPI-style microservice).
- Renderer focus subscription endpoint not defined; propose adding a lightweight focus text feed (poll/WS) the Braille adapter can consume.
- Policy/consent scopes for Braille to be added parallel to BCI scopes.
