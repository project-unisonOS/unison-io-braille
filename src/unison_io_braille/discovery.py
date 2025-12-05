import logging
from typing import Iterable, List, Tuple, Dict

from .interfaces import DeviceInfo

logger = logging.getLogger("unison-io-braille.discovery")

try:
    import hid  # type: ignore
except Exception:  # pragma: no cover
    hid = None

try:
    from bleak import BleakScanner  # type: ignore
except Exception:  # pragma: no cover
    BleakScanner = None


# Known VID/PID → driver key (placeholder; to be filled with real devices)
KNOWN_USB_DEVICES: List[Tuple[str, str | None, str]] = [
    # Freedom Scientific (Focus Blue line; sourced from public BRLTTY tables)
    ("0x05f3", "0x0007", "focus-generic"),  # Focus 14 Blue (14 cells)
    ("0x05f3", "0x0008", "focus-generic"),  # Focus 40 Blue
    ("0x05f3", "0x0009", "focus-generic"),  # Focus 80 Blue
    ("0x05f3", None, "focus-generic"),
    # Handy Tech Elektronik (generic fallback)
    ("0x1fe4", None, "handytech"),
    # HIMS (various models)
    ("0x2001", None, "hims"),
]

# Capability hints (cells, rows, columns) for known PIDs
CAPABILITY_HINTS: Dict[str, Dict[str, int]] = {
    "0x0007": {"cells": 14, "rows": 1, "cols": 14},
    "0x0008": {"cells": 40, "rows": 1, "cols": 40},
    "0x0009": {"cells": 80, "rows": 1, "cols": 80},
}


def enumerate_usb() -> Iterable[DeviceInfo]:
    if hid is None:
        logger.info("hidapi_not_available; skipping USB scan")
        return []
    devices = []
    try:
        for d in hid.enumerate():  # type: ignore[attr-defined]
            vid = f"0x{d['vendor_id']:04x}"
            pid = f"0x{d['product_id']:04x}"
            name = d.get("product_string") or "unknown"
            key = next((k for v, p, k in KNOWN_USB_DEVICES if v == vid and (p is None or p == pid)), None)
            caps = {"driver_key": key}
            if pid in CAPABILITY_HINTS:
                caps.update(CAPABILITY_HINTS[pid])
            devices.append(DeviceInfo(id=f"usb:{vid}:{pid}", transport="usb", vid=vid, pid=pid, name=name, capabilities=caps))
    except Exception as exc:  # pragma: no cover
        logger.warning("usb_scan_failed %s", exc)
    return devices


async def enumerate_bluetooth() -> Iterable[DeviceInfo]:
    if BleakScanner is None:
        logger.info("bleak_not_available; skipping BT scan")
        return []
    devices = []
    try:
        found = await BleakScanner.discover(timeout=4.0)
        for d in found:
            devices.append(DeviceInfo(id=f"bt:{d.address}", transport="bt", name=d.name, capabilities={"driver_key": None}))
    except Exception as exc:  # pragma: no cover
        logger.warning("bt_scan_failed %s", exc)
    return devices
