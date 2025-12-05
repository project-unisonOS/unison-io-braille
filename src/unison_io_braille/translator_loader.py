import importlib.resources as pkg_resources
from pathlib import Path
from typing import Dict, Any, Sequence

import yaml

from .interfaces import BrailleCells, BrailleCell
from .translator import SimpleTranslator, _make_dots

try:
    import louis  # type: ignore
except Exception:  # pragma: no cover
    louis = None


def load_table(name: str) -> Dict[str, Any]:
    """
    Load a Braille table definition by name from bundled YAML files.
    """
    try:
        with pkg_resources.files("unison_io_braille.tables").joinpath(f"{name}.yaml").open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except FileNotFoundError:
        return {}


class TableTranslator(SimpleTranslator):
    """Translator backed by YAML tables or liblouis if available."""

    def __init__(self, table_name: str = "ueb_grade1") -> None:
        self.table_name = table_name
        table_def = load_table(table_name)
        mapping = table_def.get("mapping", {})
        dots = int(table_def.get("dots", 6)) if table_def else 6
        mapped: Dict[str, Sequence[int]] = {k: tuple(v) for k, v in mapping.items()} if mapping else None
        super().__init__(table=mapped, eight_dot=dots == 8)

    def text_to_cells(self, text: str, config: Dict[str, Any] | None = None) -> BrailleCells:
        if louis:
            try:
                cells = louis.translate([self.table_name], text, mode=louis.dotsIO)  # type: ignore[attr-defined]
                # louis returns list of integers representing dot patterns per cell
                dots = []
                for c in cells[0]:
                    bits = []
                    for i in range(1, 9):
                        if c & (1 << (i - 1)):
                            bits.append(i)
                    dots.append(_make_dots(bits, 8 if self.eight_dot else 6))
                return BrailleCells(rows=1, cols=len(dots), cells=dots, cursor_position=len(dots) - 1 if dots else None)
            except Exception:
                pass
        return super().text_to_cells(text, config)

    def cells_to_text(self, cells: BrailleCells, config: Dict[str, Any] | None = None) -> str:
        return super().cells_to_text(cells, config)
