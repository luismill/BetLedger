"""Helpers for exporting and importing CSV files."""
from __future__ import annotations

import csv
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path
from typing import Iterable, List, Type, TypeVar

T = TypeVar("T")


def export_dataclasses(path: Path, rows: Iterable[object]) -> None:
    rows = list(rows)
    if not rows:
        path.write_text("")
        return
    sample = rows[0]
    if not is_dataclass(sample):
        raise TypeError("Rows must be dataclass instances")
    headers = [f.name for f in fields(sample)]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def import_dataclasses(path: Path, cls: Type[T]) -> List[T]:
    if not path.exists():
        return []
    if not is_dataclass(cls):
        raise TypeError("cls must be a dataclass")
    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        result = []
        for raw in reader:
            kwargs = {name: raw[name] for name in raw}
            result.append(cls(**kwargs))  # type: ignore[arg-type]
        return result
