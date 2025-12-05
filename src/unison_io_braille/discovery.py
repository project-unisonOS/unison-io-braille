import logging
from typing import Iterable, List, Tuple

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
    # Freedom Scientific (e.g., Focus Blue line)
    ("0x05f3", "0x0007", "focus-generic"),
    ("0x05f3", None, "focus-generic"),
    # Handy Tech Elektronik
    ("0x1fe4", None, "handytech"),
    # HIMS (various models)
    ("0x2001", None, "hims"),
]


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
            devices.append(DeviceInfo(id=f"usb:{vid}:{pid}", transport="usb", vid=vid, pid=pid, name=name, capabilities={"driver_key": key}))
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
