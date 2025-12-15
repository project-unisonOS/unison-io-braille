# unison-io-braille

Braille input/output service for UnisonOS. Handles device discovery (USB/Bluetooth), packet parsing, Braille translation, and bridging to the Unison event bus so Braille keyboards/displays are first-class modalities from first boot.

## Status
Scaffolding repo. No device support shipped yet.

## Quick orientation
- `docs/INTEGRATION_OVERVIEW.md` — how Braille slots into existing Unison I/O, event schemas, and onboarding.
- `docs/BRAILLE_ARCHITECTURE.md` — proposed architecture (drivers, translator, adapter, onboarding helper).
- `docs/BRAILLE_ONBOARDING.md` — first-boot/onboarding flow considerations.
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

## Contributing
Add new device drivers by implementing the `BrailleDeviceDriver` interface and registering it with the driver registry. Translation tables should be added as configs or plugins in `src/translator/tables/`.
