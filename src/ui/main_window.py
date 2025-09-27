"""Main window with side navigation."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QWidget,
)

from .calculator_view import CalculatorView
from .operations_view import OperationsView
from .accounts_view import AccountsView
from .dashboard_view import DashboardView
from .incentives_view import IncentivesView
from .compare_view import CompareView
from .glossary_view import GlossaryView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BetLedger")
        container = QWidget()
        layout = QHBoxLayout(container)
        self.menu = QListWidget()
        self.menu.setFixedWidth(180)
        for label in [
            "Dashboard",
            "Calculadora",
            "Operaciones",
            "Cuentas",
            "Incentivos",
            "Comparador",
            "Glosario",
        ]:
            item = QListWidgetItem(label)
            self.menu.addItem(item)
        self.menu.currentRowChanged.connect(self._change_view)

        self.stack = QStackedWidget()
        self.stack.addWidget(DashboardView())
        self.stack.addWidget(CalculatorView())
        self.stack.addWidget(OperationsView())
        self.stack.addWidget(AccountsView())
        self.stack.addWidget(IncentivesView())
        self.stack.addWidget(CompareView())
        self.stack.addWidget(GlossaryView())

        layout.addWidget(self.menu)
        layout.addWidget(self.stack, stretch=1)
        self.setCentralWidget(container)
        self.menu.setCurrentRow(0)

    def _change_view(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
