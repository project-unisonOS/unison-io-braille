from typing import Dict, Optional, Type

from .interfaces import BrailleDeviceDriver
from .simulated_driver import SimulatedBrailleDriver
from .generic_hid import GenericHIDDriver
from .drivers.focus import FocusBrailleDriver


class BrailleDeviceDriverRegistry:
    """Registry for mapping device identifiers to drivers."""

    def __init__(self) -> None:
        self._drivers: Dict[str, Type[BrailleDeviceDriver]] = {}
        self.register("sim", SimulatedBrailleDriver)
        self.register("generic-hid", GenericHIDDriver)
        self.register("focus-generic", FocusBrailleDriver)

    def register(self, key: str, driver: Type[BrailleDeviceDriver]) -> None:
        self._drivers[key] = driver

    def get(self, key: str) -> Optional[Type[BrailleDeviceDriver]]:
        return self._drivers.get(key)
