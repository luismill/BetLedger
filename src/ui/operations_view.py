"""Operations table placeholder."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..services.operation_service import OperationService


class OperationsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service = OperationService()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Gestione operaciones en la vista avanzada"))
