from typing import Iterable, List

from .interfaces import BrailleDeviceDriver, BrailleEvent, BrailleCells, DeviceInfo


class SimulatedBrailleDriver(BrailleDeviceDriver):
    """
    Simple simulated driver: collects sent cells, parses bytes as ASCII characters for events.
    Intended for tests and dev without hardware.
    """

    def __init__(self) -> None:
        self.opened = False
        self.device: DeviceInfo | None = None
        self.sent: List[BrailleCells] = []
        self.received_packets: List[bytes] = []

    def open(self, device: DeviceInfo) -> None:
        self.device = device
        self.opened = True

    def close(self) -> None:
        self.opened = False

    def send_cells(self, cells: BrailleCells) -> None:
        self.sent.append(cells)

    def on_packet(self, data: bytes) -> Iterable[BrailleEvent]:
        self.received_packets.append(data)
        try:
            text = data.decode(errors="ignore").strip()
        except Exception:
            text = ""
        if text:
            yield BrailleEvent(type="text", keys=(), text=text, device_id=self.device.id if self.device else None)
