from typing import Dict, Any, Sequence, List, Tuple

from .interfaces import BrailleCells, BrailleCell, Translator


def _make_dots(on: Sequence[int], total_dots: int) -> BrailleCell:
    dots = [False] * total_dots
    for d in on:
        idx = d - 1
        if 0 <= idx < total_dots:
            dots[idx] = True
    return BrailleCell(dots=dots)


class SimpleTranslator(Translator):
    """
    Minimal translator with a small ASCII→Braille table (UEB Grade 1 sketch).
    Supports multi-character tokens via greedy matching.
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
        self._tokens_sorted = sorted(self.table.keys(), key=len, reverse=True)
        total_dots = 8 if self.eight_dot else 6
        self._reverse = {tuple(sorted(v)): k for k, v in self.table.items()}
        self._total_dots = total_dots

    def _token_to_cell(self, token: str) -> BrailleCell:
        dots_on = self.table.get(token.lower(), tuple())
        return _make_dots(dots_on, self._total_dots)

    def _greedy_tokenize(self, text: str) -> List[str]:
        tokens: List[str] = []
        i = 0
        lower = text.lower()
        while i < len(text):
            matched = None
            for tok in self._tokens_sorted:
                if lower.startswith(tok, i):
                    matched = tok
                    break
            if matched:
                tokens.append(matched)
                i += len(matched)
            else:
                tokens.append(text[i])
                i += 1
        return tokens

    def text_to_cells(self, text: str, config: Dict[str, Any] | None = None) -> BrailleCells:
        tokens = self._greedy_tokenize(text)
        cells = [self._token_to_cell(tok) for tok in tokens]
        return BrailleCells(rows=1, cols=len(cells), cells=cells, cursor_position=len(cells) - 1 if cells else None)

    def cells_to_text(self, cells: BrailleCells, config: Dict[str, Any] | None = None) -> str:
        out = []
        for cell in cells.cells:
            on = tuple(i + 1 for i, v in enumerate(cell.dots) if v)
            out.append(self._reverse.get(on, "?"))
        return "".join(out)
