import importlib.resources as pkg_resources
from pathlib import Path
from typing import Dict, Any, Sequence

import yaml

from .interfaces import BrailleCells, BrailleCell
from .translator import SimpleTranslator


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
    """Translator backed by YAML tables; falls back to SimpleTranslator defaults."""

    def __init__(self, table_name: str = "ueb_grade1") -> None:
        table_def = load_table(table_name)
        mapping = table_def.get("mapping", {})
        dots = int(table_def.get("dots", 6)) if table_def else 6
        mapped: Dict[str, Sequence[int]] = {k: tuple(v) for k, v in mapping.items()} if mapping else None
        super().__init__(table=mapped, eight_dot=dots == 8)

    def text_to_cells(self, text: str, config: Dict[str, Any] | None = None) -> BrailleCells:
        return super().text_to_cells(text, config)

    def cells_to_text(self, cells: BrailleCells, config: Dict[str, Any] | None = None) -> str:
        return super().cells_to_text(cells, config)
