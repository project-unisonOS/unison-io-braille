# unison-io-braille

Braille input/output service for UnisonOS. Handles device discovery (USB/Bluetooth), packet parsing, Braille translation, and bridging to the Unison event bus so Braille keyboards/displays are first-class modalities from first boot.

## Status
Planning scaffold. No device support yet — see `docs/MILESTONES.md` for the execution plan.

## Quick orientation
- `docs/INTEGRATION_OVERVIEW.md` — how Braille slots into existing Unison I/O, event schemas, and onboarding.
- `docs/BRAILLE_ARCHITECTURE.md` — proposed architecture (drivers, translator, adapter, onboarding helper).
- `docs/BRAILLE_ONBOARDING.md` — first-boot/onboarding flow considerations.
- `docs/MILESTONES.md` — phased issues/epics to implement.
- `src/` — core interfaces, translator, discovery stubs, simulated driver.
- `src/unison_io_braille/server.py` — FastAPI skeleton with `/health`, `/ready`, `/metrics`, `/braille/translate`, and `/braille/output` (WS) for diagnostics.

## Dev setup (placeholder)
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
pytest
```

## Auth and orchestrator integration
- Outbound event posts include `Authorization: Bearer $UNISON_ORCH_AUTH_TOKEN` if set.
- Incoming requests can be validated against a JWKS (`UNISON_AUTH_JWKS_URL`, cached/auto-refreshed) or OAuth2 introspection (`UNISON_AUTH_INTROSPECT_URL` + optional `UNISON_AUTH_CLIENT_ID`/`UNISON_AUTH_CLIENT_SECRET`). Falls back to scope strings for local/dev.

## HID output
- USB devices use hidapi for writes; drivers call async writes to avoid blocking the event loop.
- Focus/HandyTech/HIMS drivers emit vendor-shaped output reports (report IDs 0x08/0x20/0x30 with cursor + dot masks).

## Remaining Braille tasks (next phases)
- Harden Braille output path to real devices: unblock platform udev/USB permissions and verify writes on hardware.
- Implement Braille output subscription to renderer/onboarding focus feed (WS/poll) with panning/routing behavior.
- Finalize Braille event schema (`braille.input`, `braille.output`) and align with orchestrator envelopes.
- Expand translation tables (UEB Grade 2 completeness, computer Braille, more languages) and add table selection per user/profile.
- Add more vendor drivers (HumanWare/Brailliant, additional Focus/HIMS models) and richer HID parsing/output per spec.
- Add settings/context storage for per-person defaults (table, 6/8-dot, cursor prefs, HID mappings).
- Integrate Braille-only onboarding flow and shell navigation mapping; add end-to-end tests.
- Production auth: replace stub/introspection with orchestrator JWKS/consent integration and tighten scope policies.

## Contributing
Open issues/PRs against the milestones in `docs/MILESTONES.md`. Add new device drivers by implementing the `BrailleDeviceDriver` interface and registering it with the driver registry. Translation tables should be added as configs or plugins in `src/translator/tables/`.
