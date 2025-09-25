"""Dashboard view summarising KPIs."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..services.report_service import ReportService


class DashboardView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service = ReportService()
        layout = QVBoxLayout(self)
        self.label = QLabel()
        layout.addWidget(QLabel("Indicadores clave"))
        layout.addWidget(self.label)
        layout.addStretch(1)
        self.refresh()

    def refresh(self) -> None:
        kpis = self.service.kpis()
        text = "\n".join(f"{key}: {value:.2f}" for key, value in kpis.items())
        self.label.setText(text)
