from unison_io_braille.drivers.handytech import HandyTechDriver
from unison_io_braille.drivers.hims import HimsBrailleDriver
from unison_io_braille.interfaces import DeviceInfo, BrailleCells, BrailleCell


def test_handytech_driver_parses_text_and_routing():
    drv = HandyTechDriver()
    drv.open(DeviceInfo(id="ht1", transport="usb"))
    events = list(drv.on_packet(bytes([0x01, ord("b")])))
    assert any(e.type == "text" and e.text == "b" for e in events)
    routing = list(drv.on_packet(bytes([0x02, 3])))
    assert any(e.type == "routing" and "cell-3" in e.keys for e in routing)
    cells = BrailleCells(rows=1, cols=1, cells=[BrailleCell([True, False, False, False, False, False])])
    drv.send_cells(cells)
    assert drv.last_output and drv.last_output[0] == 0x10


def test_hims_driver_parses_nav_and_output():
    drv = HimsBrailleDriver()
    drv.open(DeviceInfo(id="hims1", transport="usb"))
    events = list(drv.on_packet(bytes([0x01, 0x0D, ord("c")])))
    assert any(e.type == "nav" and "enter" in e.keys for e in events)
    assert any(e.type == "text" and e.text == "c" for e in events)
    cells = BrailleCells(rows=1, cols=1, cells=[BrailleCell([True, True, False, False, False, False])])
    drv.send_cells(cells)
    assert drv.last_output and drv.last_output[0] == 0x11
