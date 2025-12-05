# unison-io-braille

Braille input/output service for UnisonOS. Handles device discovery (USB/Bluetooth), packet parsing, Braille translation, and bridging to the Unison event bus so Braille keyboards/displays are first-class modalities from first boot.

## Status
Planning scaffold. No device support yet — see `docs/MILESTONES.md` for the execution plan.

## Quick orientation
- `docs/INTEGRATION_OVERVIEW.md` — how Braille slots into existing Unison I/O, event schemas, and onboarding.
- `docs/BRAILLE_ARCHITECTURE.md` — proposed architecture (drivers, translator, adapter, onboarding helper).
- `docs/BRAILLE_ONBOARDING.md` — first-boot/onboarding flow considerations.
- `docs/MILESTONES.md` — phased issues/epics to implement.
- `src/` — placeholders for core interfaces (device manager, driver, translator, adapter).

## Dev setup (placeholder)
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
pytest
```

## Contributing
Open issues/PRs against the milestones in `docs/MILESTONES.md`. Add new device drivers by implementing the `BrailleDeviceDriver` interface and registering it with the driver registry. Translation tables should be added as configs or plugins in `src/translator/tables/`.
