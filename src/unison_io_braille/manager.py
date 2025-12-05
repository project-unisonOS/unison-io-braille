from typing import Dict, Optional, Type

from .interfaces import DeviceInfo, BrailleDeviceDriver


class BrailleDeviceDriverRegistry:
    """Registry for mapping device identifiers to drivers."""

    def __init__(self) -> None:
        self._drivers: Dict[str, Type[BrailleDeviceDriver]] = {}

    def register(self, key: str, driver: Type[BrailleDeviceDriver]) -> None:
        self._drivers[key] = driver

    def get(self, key: str) -> Optional[Type[BrailleDeviceDriver]]:
        return self._drivers.get(key)


class BrailleDeviceManager:
    """
    Placeholder manager responsible for discovery and lifecycle.
    Real discovery (USB/BT) will be added later.
    """

    def __init__(self, registry: BrailleDeviceDriverRegistry) -> None:
        self.registry = registry
        self.active: Dict[str, BrailleDeviceDriver] = {}

    def attach(self, device: DeviceInfo) -> None:
        key = f"{device.vid}:{device.pid}" if device.vid and device.pid else device.id
        driver_cls = self.registry.get(key)
        if not driver_cls:
            return
        driver = driver_cls()
        driver.open(device)
        self.active[device.id] = driver

    def detach(self, device_id: str) -> None:
        drv = self.active.pop(device_id, None)
        if drv:
            drv.close()
