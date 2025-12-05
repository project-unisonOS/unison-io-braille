from unison_io_braille.drivers.focus import FocusBrailleDriver
from unison_io_braille.interfaces import DeviceInfo, BrailleCells, BrailleCell


def test_focus_driver_parses_nav_and_text():
    drv = FocusBrailleDriver()
    drv.open(DeviceInfo(id="focus1", transport="usb", vid="0x05f3", pid="0x0007"))
    # Report ID 0x01, payload: 'a' and nav code 0x0D (enter)
    events = list(drv.on_packet(bytes([0x01, ord("a"), 0x0D])))
    assert any(e.type == "text" and e.text == "a" for e in events)
    assert any(e.type == "nav" and "enter" in e.keys for e in events)


def test_focus_driver_parses_chord_and_routing():
    drv = FocusBrailleDriver()
    drv.open(DeviceInfo(id="focus1", transport="usb"))
    # Report ID 0x01, high bit marks chord, bits 0/2/3 set -> dot1, dot3, dot4
    chord_events = list(drv.on_packet(bytes([0x01, 0x8D])))
    assert any(e.type == "chord" and {"dot1", "dot3", "dot4"} == set(e.keys) for e in chord_events)
    # Report ID 0x02, routing for cell 5
    routing = list(drv.on_packet(bytes([0x02, 5])))
    assert any(e.type == "routing" and "cell-5" in e.keys for e in routing)


def test_focus_driver_sends_cells_masked():
    drv = FocusBrailleDriver()
    drv.open(DeviceInfo(id="focus1", transport="usb"))
    cells = BrailleCells(rows=1, cols=2, cells=[BrailleCell([True, False, True, False, False, False, False, False]), BrailleCell([False, False, False, False, False, False, False, False])])
    drv.send_cells(cells)
    assert drv.last_output is not None
    # Report id 0x08, count 2, cursor byte, first mask bits 0 and 2 -> 0b00000101 = 5
    assert drv.last_output[0] == 0x08
    assert drv.last_output[1] == 2
    assert drv.last_output[3] == 0x05


def test_focus_driver_writes_to_transport():
    class StubWriter:
        def __init__(self):
            self.written = []

        def write(self, data: bytes):
            self.written.append(bytes(data))

    drv = FocusBrailleDriver()
    drv.set_output_writer(StubWriter())
    drv.open(DeviceInfo(id="focus1", transport="usb"))
    drv.send_cells(BrailleCells(rows=1, cols=1, cells=[BrailleCell([True, False, False, False, False, False, False, False])]))
    assert drv.writer.written  # type: ignore[attr-defined]
