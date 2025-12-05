from typing import Iterable

from ..interfaces import BrailleDeviceDriver, DeviceInfo, BrailleEvent, BrailleCells


class FocusBrailleDriver(BrailleDeviceDriver):
    """
    Template driver for Freedom Scientific Focus Braille displays.
    This is a simplified stub: it treats ASCII bytes as text and certain control bytes as nav keys.
    Extend with real HID report parsing as specs become available.
    """

    NAV_MAP = {
        0x0D: ("nav", ["enter"]),
        0x08: ("nav", ["back"]),
        0x1B: ("nav", ["escape"]),
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

    def on_packet(self, data: bytes) -> Iterable[BrailleEvent]:
        for b in data:
            if b in self.NAV_MAP:
                etype, keys = self.NAV_MAP[b]
                yield BrailleEvent(type=etype, keys=keys, device_id=self.device.id if self.device else None)
            elif 32 <= b <= 126:
                yield BrailleEvent(type="text", keys=(), text=chr(b), device_id=self.device.id if self.device else None)
