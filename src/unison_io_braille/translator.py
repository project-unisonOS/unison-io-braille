from typing import Dict, Any, Sequence

from .interfaces import BrailleCells, BrailleCell, Translator


class SimpleTranslator(Translator):
    """
    Minimal translator with a small ASCII→Braille table (UEB Grade 1 sketch).
    This is intentionally small; full tables should be plugged in later.
    """

    DEFAULT_TABLE: Dict[str, Sequence[int]] = {
        "a": (1,),
        "b": (1, 2),
        "c": (1, 4),
        "d": (1, 4, 5),
        "e": (1, 5),
        "f": (1, 2, 4),
        "g": (1, 2, 4, 5),
        "h": (1, 2, 5),
        "i": (2, 4),
        "j": (2, 4, 5),
        " ": tuple(),
    }

    def __init__(self, table: Dict[str, Sequence[int]] | None = None, eight_dot: bool = False) -> None:
        self.table = table or self.DEFAULT_TABLE
        self.eight_dot = eight_dot

    def _cell_from_char(self, ch: str) -> BrailleCell:
        dots_on = self.table.get(ch.lower(), tuple())
        total_dots = 8 if self.eight_dot else 6
        dots = [False] * total_dots
        for d in dots_on:
            idx = d - 1
            if 0 <= idx < total_dots:
                dots[idx] = True
        return BrailleCell(dots=dots)

    def text_to_cells(self, text: str, config: Dict[str, Any] | None = None) -> BrailleCells:
        cells = [self._cell_from_char(ch) for ch in text]
        return BrailleCells(rows=1, cols=len(cells), cells=cells, cursor_position=len(cells) - 1 if cells else None)

    def cells_to_text(self, cells: BrailleCells, config: Dict[str, Any] | None = None) -> str:
        # Very naive reverse lookup for test purposes
        reverse = {tuple(sorted(v)): k for k, v in self.table.items()}
        out = []
        for cell in cells.cells:
            on = tuple(i + 1 for i, v in enumerate(cell.dots) if v)
            out.append(reverse.get(on, "?"))
        return "".join(out)
