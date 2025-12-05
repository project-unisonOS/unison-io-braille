from typing import Iterable, List

from ..interfaces import BrailleDeviceDriver, DeviceInfo, BrailleEvent, BrailleCells


class HandyTechDriver(BrailleDeviceDriver):
    """
    Simple HandyTech placeholder driver.
    Parses a lightweight packet format:
      - 0x01 -> key payload (ASCII or nav codes)
      - 0x02 -> routing key index
    Real HandyTech protocols (HTCom) are richer; this provides a template for wiring.
    """

    NAV_MAP = {
        0x0D: ("nav", ["enter"]),
        0x08: ("nav", ["back"]),
        0x09: ("nav", ["tab"]),
    }

    def __init__(self) -> None:
        self.device: DeviceInfo | None = None
        self.last_output: bytes | None = None

    def open(self, device: DeviceInfo) -> None:
        self.device = device

    def close(self) -> None:
        self.device = None

    def send_cells(self, cells: BrailleCells) -> None:
        # HandyTech displays accept dot bitmasks per cell; represent with report 0x10 as placeholder.
        report = bytearray([0x10, len(cells.cells)])
        for cell in cells.cells:
            mask = 0
            for i, v in enumerate(cell.dots):
                if v:
                    mask |= 1 << i
            report.append(mask)
        self.last_output = bytes(report)

    def _make_event(self, etype: str, keys: List[str], text: str | None = None) -> BrailleEvent:
        return BrailleEvent(type=etype, keys=keys, text=text, device_id=self.device.id if self.device else None)

    def on_packet(self, data: bytes) -> Iterable[BrailleEvent]:
        if not data:
            return []
        report_id = data[0]
        payload = data[1:]
        events: List[BrailleEvent] = []
        if report_id == 0x01:
            for b in payload:
                if b in self.NAV_MAP:
                    etype, keys = self.NAV_MAP[b]
                    events.append(self._make_event(etype, list(keys)))
                elif 32 <= b <= 126:
                    events.append(self._make_event("text", [], text=chr(b)))
        elif report_id == 0x02:
            for idx in payload:
                events.append(self._make_event("routing", [f"cell-{idx}"]))
        return events
