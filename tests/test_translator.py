from unison_io_braille.translator import SimpleTranslator
from unison_io_braille.interfaces import BrailleCells, BrailleCell


def test_text_to_cells_basic():
    translator = SimpleTranslator()
    cells = translator.text_to_cells("ab")
    assert isinstance(cells, BrailleCells)
    assert len(cells.cells) == 2
    assert cells.cells[0].dots[0]  # dot1 for 'a'
    assert cells.cells[1].dots[1]  # dot2 for 'b'


def test_cells_to_text_roundtrip():
    translator = SimpleTranslator()
    cells = BrailleCells(rows=1, cols=2, cells=[BrailleCell([True, False, False, False, False, False]), BrailleCell([True, True, False, False, False, False])])
    text = translator.cells_to_text(cells)
    assert text == "ab"
