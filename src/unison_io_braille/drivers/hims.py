from typing import Iterable, List

from ..interfaces import BrailleDeviceDriver, DeviceInfo, BrailleEvent, BrailleCells


class HimsBrailleDriver(BrailleDeviceDriver):
    """
    Simple HIMS placeholder driver (e.g., BrailleSense/BrailleEdge).
    Interprets ASCII payloads and a small nav map; routing keys via 0x02.
    """

    NAV_MAP = {
        0x0D: ("nav", ["enter"]),
        0x08: ("nav", ["back"]),
        0x1B: ("nav", ["escape"]),
        0x20: ("nav", ["space"]),
    }

    def __init__(self) -> None:
        self.device: DeviceInfo | None = None
        self.last_output: bytes | None = None
        self.writer = None

    def open(self, device: DeviceInfo) -> None:
        self.device = device

    def close(self) -> None:
        self.device = None
        self.writer = None

    def set_output_writer(self, writer) -> None:
        self.writer = writer

    def send_cells(self, cells: BrailleCells) -> None:
        # Simplified output frame; actual HIMS uses custom protocols.
        report = bytearray([0x30, len(cells.cells)])
        cursor = 0xFF if cells.cursor_position is None else int(cells.cursor_position)
        report.append(cursor)
        for cell in cells.cells:
            mask = 0
            for i, v in enumerate(cell.dots):
                if v:
                    mask |= 1 << i
            report.append(mask)
        self.last_output = bytes(report)
        if self.writer:
            write = getattr(self.writer, "write_async", None) or getattr(self.writer, "write", None)
            if write:
                write(self.last_output)

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
