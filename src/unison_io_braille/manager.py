from typing import Dict, Optional, Type

from .interfaces import DeviceInfo, BrailleDeviceDriver
from .driver_registry import BrailleDeviceDriverRegistry


class BrailleDeviceManager:
    """
    Placeholder manager responsible for discovery and lifecycle.
    Real discovery (USB/BT) will be added later.
    """

    def __init__(self, registry: BrailleDeviceDriverRegistry) -> None:
        self.registry = registry
        self.active: Dict[str, BrailleDeviceDriver] = {}

    def attach(self, device: DeviceInfo) -> None:
        key = device.capabilities.get("driver_key") if device.capabilities else None
        key = key or (f"{device.vid}:{device.pid}" if device.vid and device.pid else device.id)
        driver_cls = self.registry.get(key) or self.registry.get("generic-hid")
        if not driver_cls:
            return
        driver = driver_cls()
        driver.open(device)
        self.active[device.id] = driver

    def detach(self, device_id: str) -> None:
        drv = self.active.pop(device_id, None)
        if drv:
            drv.close()
