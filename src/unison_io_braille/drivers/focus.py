from typing import Iterable, List

from ..interfaces import BrailleDeviceDriver, DeviceInfo, BrailleEvent, BrailleCells


class FocusBrailleDriver(BrailleDeviceDriver):
    """
    Template driver for Freedom Scientific Focus Braille displays.
    Parses simple HID-like input reports:
      - Report ID 0x01, payload bytes representing keycodes.
      - ASCII range -> text events.
      - NAV_MAP for common navigation keys.
    Extend with real report maps/output reports as specs become available.
    """

    NAV_MAP = {
        0x0D: ("nav", ["enter"]),
        0x08: ("nav", ["back"]),
        0x1B: ("nav", ["escape"]),
        0x25: ("nav", ["left"]),   # hypothetical arrow codes
        0x26: ("nav", ["up"]),
        0x27: ("nav", ["right"]),
        0x28: ("nav", ["down"]),
    }

    def __init__(self) -> None:
        self.device: DeviceInfo | None = None

    def open(self, device: DeviceInfo) -> None:
        self.device = device

    def close(self) -> None:
        self.device = None

    def send_cells(self, cells: BrailleCells) -> None:
        # TODO: implement HID output reports to update display cells
        return

    def _parse_report(self, report: bytes) -> Iterable[BrailleEvent]:
        if not report:
            return []
        report_id = report[0]
        payload = report[1:] if len(report) > 1 else b""
        events: List[BrailleEvent] = []
        if report_id == 0x01:
            for b in payload:
                if b in self.NAV_MAP:
                    etype, keys = self.NAV_MAP[b]
                    events.append(BrailleEvent(type=etype, keys=keys, device_id=self.device.id if self.device else None))
                elif 32 <= b <= 126:
                    events.append(BrailleEvent(type="text", keys=(), text=chr(b), device_id=self.device.id if self.device else None))
        return events

    def on_packet(self, data: bytes) -> Iterable[BrailleEvent]:
        return self._parse_report(data)
