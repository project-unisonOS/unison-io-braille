# Braille I/O Milestones & Issues

## Milestone 1 – Repo setup & architecture (this pass)
- [x] Scaffold repo (`README`, docs, interfaces).
- [ ] Decide runtime stack (Python FastAPI aligning with other `unison-io-*` services).
- [ ] Add CI (lint+pytest skeleton) and constraints/requirements.

## Milestone 2 – Translation layer & simulation
- Implement `BrailleTranslator` with core tables: UEB Grade 1/2, 6/8-dot (config-driven).
- Add simulated Braille device driver (feeds canned packets, accepts cell writes).
- Unit tests for translator and simulated driver; wire into CI.

## Milestone 3 – Discovery & first driver
- Implement USB/Bluetooth discovery (hidapi/libusb + Bleak/BlueZ).
- Driver registry with generic HID + first real device driver (e.g., HumanWare or Focus line).
- Emit `caps.report` and input envelopes; add `/braille/raw` WS for diagnostics.

## Milestone 4 – Onboarding integration
- Braille-only onboarding helper with minimal menu.
- Focus/text feed subscription from renderer; render to display with panning and routing.
- Map Braille keys to navigation + text for shell/onboarding.

## Milestone 5 – Hardening & accessibility UX
- Reconnect/backoff, better error handling, multiple device support.
- Expand table library and device coverage.
- Policy/consent scopes finalized; settings UI hooks; more tests.

## Issue backlog (suggested)
- Define Braille event schema (`braille.input`, `braille.output`) aligned to EventEnvelope.
- Choose transport libs and base image dependencies (hidapi/libusb/Bleak) compatible with devstack.
- Add policy scopes: `braille.device.pair`, `braille.input.read`, `braille.output.write`, `braille.profile.manage`.
- Implement focus/text feed endpoint (renderer or dedicated adapter WS).
- Add calibration/config storage in context service (per-person table, 6/8-dot, cursor prefs).
