from typing import Iterable, List

from ..interfaces import BrailleDeviceDriver, DeviceInfo, BrailleEvent, BrailleCells


class FocusBrailleDriver(BrailleDeviceDriver):
    """
    Template driver for Freedom Scientific Focus Braille displays.
    Parses simple HID-like input reports:
      - Report ID 0x01, payload bytes representing keycodes.
      - Report ID 0x02, payload bytes representing routing key index.
      - ASCII range -> text events; bitmask -> chorded dot keys.
      - NAV_MAP for common navigation/panning keys.
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
        0x5C: ("nav", ["pan-left"]),
        0x5D: ("nav", ["pan-right"]),
    }

    DOT_KEYS = tuple(f"dot{i}" for i in range(1, 9))

    def __init__(self) -> None:
        self.device: DeviceInfo | None = None

    def open(self, device: DeviceInfo) -> None:
        self.device = device

    def close(self) -> None:
        self.device = None

    def send_cells(self, cells: BrailleCells) -> None:
        # TODO: implement HID output reports to update display cells
        return

    def _make_event(self, etype: str, keys: List[str], text: str | None = None) -> BrailleEvent:
        return BrailleEvent(type=etype, keys=keys, text=text, device_id=self.device.id if self.device else None)

    def _decode_dots(self, mask: int) -> List[str]:
        return [self.DOT_KEYS[i] for i in range(8) if mask & (1 << i)]

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
                    events.append(self._make_event(etype, list(keys)))
                elif b & 0x80 and (b & 0x7F):  # high bit set -> chord mask, remaining bits = dots
                    dots = self._decode_dots(b & 0x7F)
                    events.append(self._make_event("chord", dots))
                elif 32 <= b <= 126:
                    events.append(self._make_event("text", [], text=chr(b)))
        elif report_id == 0x02:
            for idx in payload:
                events.append(self._make_event("routing", [f"cell-{idx}"]))
        return events

    def on_packet(self, data: bytes) -> Iterable[BrailleEvent]:
        return self._parse_report(data)
