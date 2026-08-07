"""Shared helpers for the fleet-evals test suite."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "2026-05-18"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]


def make_run_dir(tmp_path: Path, *fixture_names: str) -> Path:
    """Create a run dir seeded with copies of the named 2026-05-18 fixtures
    (fixtures themselves stay immutable)."""
    run_dir = tmp_path / "run"
    run_dir.mkdir(exist_ok=True)
    for name in fixture_names:
        shutil.copy(FIXTURES / name, run_dir / name)
    return run_dir


def md_tables(text: str) -> list[list[list[str]]]:
    """Parse every markdown table in the document, in order.

    Returns a list of tables; each table is a list of rows; each row is a
    list of cell strings (header row included, separator rows dropped).
    """
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue  # separator row
            current.append(cells)
        else:
            if current:
                tables.append(current)
                current = []
    if current:
        tables.append(current)
    return tables


def table_as_dict(table: list[list[str]], label_map: dict[str, str] | None = None,
                  ) -> dict[str, dict[str, str]]:
    """{row_label: {column_label: cell}} with labels passed through
    ``label_map`` (identity for unmapped labels) so the legacy tables'
    'Base'/'Fine-tuned' prose and the n-way tables' raw candidate names
    compare as the same thing."""
    label_map = label_map or {}

    def m(s: str) -> str:
        return label_map.get(s, s)

    header = [m(c) for c in table[0]]
    out: dict[str, dict[str, str]] = {}
    for row in table[1:]:
        out[m(row[0])] = {header[i]: row[i] for i in range(1, len(row))}
    return out


# Maps the published 2026-05-18 tables' prose labels onto the n-way
# harness's raw candidate-name labels (documented deliberate difference).
LEGACY_LABELS = {
    "Base": "base",
    "Fine-tuned": "finetune",
    "Fine-tune": "finetune",
    "Base preferred": "base preferred",
    "Fine-tune preferred": "finetune preferred",
}
