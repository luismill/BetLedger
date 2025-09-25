"""Incentives list view."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget

from ..services.incentive_service import IncentiveService


class IncentivesView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service = IncentiveService()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Incentivos activos"))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        self.refresh()

    def refresh(self) -> None:
        self.list_widget.clear()
        for incentive in self.service.list_incentives():
            self.list_widget.addItem(f"{incentive.title} — {incentive.status}")
