from unison_io_braille.translator_loader import TableTranslator


def test_table_translator_grade1_loads():
    tr = TableTranslator("ueb_grade1")
    cells = tr.text_to_cells("ab")
    assert len(cells.cells) == 2
    assert cells.cells[0].dots[0]


def test_table_translator_8dot_flag():
    tr = TableTranslator("ueb_grade1_8dot")
    cells = tr.text_to_cells("a")
    assert len(cells.cells[0].dots) == 8


def test_grade2_contraction_greedy():
    tr = TableTranslator("ueb_grade2")
    cells = tr.text_to_cells("and")
    assert len(cells.cells) == 1  # contraction collapsed
