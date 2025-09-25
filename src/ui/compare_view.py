"""Compare opportunities view."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..services.price_compare_service import PriceCompareService


class CompareView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service = PriceCompareService()
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        load_button = QPushButton("Cargar CSV")
        load_button.clicked.connect(self.load_csv)
        layout.addWidget(QLabel("Oportunidades"))
        layout.addWidget(load_button)
        layout.addWidget(self.list_widget)

    def load_csv(self) -> None:  # pragma: no cover - interactive
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar CSV")
        if not path:
            return
        opportunities = self.service.from_csv(Path(path))
        self.list_widget.clear()
        for op in opportunities:
            self.list_widget.addItem(
                f"{op.provider_a}/{op.provider_b} {op.mercado} {op.odds_a:.2f}-{op.odds_b:.2f}"
            )
