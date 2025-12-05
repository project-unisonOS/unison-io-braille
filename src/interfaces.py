from dataclasses import dataclass
from typing import Iterable, Protocol, Sequence, Optional, Dict, Any


@dataclass
class BrailleCell:
    dots: Sequence[bool]  # length 6 or 8


@dataclass
class BrailleCells:
    rows: int
    cols: int
    cells: Sequence[BrailleCell]
    cursor_position: Optional[int] = None  # index into cells
    metadata: Dict[str, Any] | None = None


@dataclass
class BrailleEvent:
    type: str  # "chord" | "routing" | "nav" | "status" | "text"
    keys: Sequence[str]
    text: Optional[str] = None
    timestamp: float | None = None
    device_id: str | None = None


@dataclass
class DeviceInfo:
    id: str
    transport: str  # usb | bt | serial | sim
    vid: str | None = None
    pid: str | None = None
    name: str | None = None
    capabilities: Dict[str, Any] | None = None


class BrailleDeviceDriver(Protocol):
    """Interface for vendor-specific Braille device drivers."""

    def open(self, device: DeviceInfo) -> None: ...
    def close(self) -> None: ...
    def send_cells(self, cells: BrailleCells) -> None: ...
    def on_packet(self, data: bytes) -> Iterable[BrailleEvent]: ...


class BrailleTranslator(Protocol):
    """Interface for text ↔ Braille translation."""

    def text_to_cells(self, text: str, config: Dict[str, Any] | None = None) -> BrailleCells: ...
    def cells_to_text(self, cells: BrailleCells, config: Dict[str, Any] | None = None) -> str: ...
