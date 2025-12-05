from unison_io_braille.drivers.focus import FocusBrailleDriver
from unison_io_braille.interfaces import DeviceInfo


def test_focus_driver_parses_nav_and_text():
    drv = FocusBrailleDriver()
    drv.open(DeviceInfo(id="focus1", transport="usb", vid="0x05f3", pid="0x0007"))
    # Report ID 0x01, payload: 'a' and nav code 0x0D (enter)
    events = list(drv.on_packet(bytes([0x01, ord("a"), 0x0D])))
    assert any(e.type == "text" and e.text == "a" for e in events)
    assert any(e.type == "nav" and "enter" in e.keys for e in events)
