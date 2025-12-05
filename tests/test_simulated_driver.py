from unison_io_braille.simulated_driver import SimulatedBrailleDriver
from unison_io_braille.interfaces import DeviceInfo, BrailleCells, BrailleCell


def test_simulated_driver_records_cells_and_packets():
    driver = SimulatedBrailleDriver()
    device = DeviceInfo(id="sim1", transport="sim")
    driver.open(device)

    cells = BrailleCells(rows=1, cols=1, cells=[BrailleCell([True, False, False, False, False, False])])
    driver.send_cells(cells)
    assert driver.sent[-1].cells[0].dots[0] is True

    events = list(driver.on_packet(b"hi"))
    assert events
    assert events[0].text == "hi"
    driver.close()
