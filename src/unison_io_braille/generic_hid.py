from typing import Iterable

from .interfaces import BrailleDeviceDriver, DeviceInfo, BrailleEvent, BrailleCells


class GenericHIDDriver(BrailleDeviceDriver):
    """
    Stub HID driver that treats incoming bytes as text events.
    Replace with real HID report parsing per device.
    """

    def __init__(self) -> None:
        self.device: DeviceInfo | None = None

    def open(self, device: DeviceInfo) -> None:
        self.device = device

    def close(self) -> None:
        self.device = None

    def send_cells(self, cells: BrailleCells) -> None:
        # TODO: implement HID output reports for displays
        return

    def on_packet(self, data: bytes) -> Iterable[BrailleEvent]:
        try:
            text = data.decode(errors="ignore").strip()
        except Exception:
            text = ""
        if text:
            yield BrailleEvent(type="text", keys=(), text=text, device_id=self.device.id if self.device else None)
        # TODO: parse routing/nav keys from HID reports when specs are available.
