"""Simple calculator form."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..services.calculator_service import CalculatorService


class CalculatorView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service = CalculatorService()
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.stake_input = QLineEdit("25")
        self.odds_a_input = QLineEdit("2.0")
        self.odds_b_input = QLineEdit("2.1")
        self.comm_input = QLineEdit("5.0")
        self.mode_input = QComboBox()
        self.mode_input.addItems(["calificacion", "credito_no_retorno"])
        self.source_input = QComboBox()
        self.source_input.addItems(["efectivo", "credito"])

        form.addRow("Stake A", self.stake_input)
        form.addRow("Odds A", self.odds_a_input)
        form.addRow("Odds B", self.odds_b_input)
        form.addRow("Comisión B", self.comm_input)
        form.addRow("Modo", self.mode_input)
        form.addRow("Origen", self.source_input)

        self.result_box = QGroupBox("Resultados")
        grid = QGridLayout()
        self.results_labels = {
            "hedge": QLabel("0.00"),
            "exposure": QLabel("0.00"),
            "profit_a": QLabel("0.00"),
            "profit_b": QLabel("0.00"),
            "metric": QLabel("0.00"),
        }
        grid.addWidget(QLabel("Cobertura B"), 0, 0)
        grid.addWidget(self.results_labels["hedge"], 0, 1)
        grid.addWidget(QLabel("Exposición B"), 1, 0)
        grid.addWidget(self.results_labels["exposure"], 1, 1)
        grid.addWidget(QLabel("Beneficio gana A"), 2, 0)
        grid.addWidget(self.results_labels["profit_a"], 2, 1)
        grid.addWidget(QLabel("Beneficio gana B"), 3, 0)
        grid.addWidget(self.results_labels["profit_b"], 3, 1)
        grid.addWidget(QLabel("Métrica"), 4, 0)
        grid.addWidget(self.results_labels["metric"], 4, 1)
        self.result_box.setLayout(grid)

        self.calculate_button = QPushButton("Calcular")
        self.calculate_button.clicked.connect(self.calculate)

        layout.addLayout(form)
        layout.addWidget(self.calculate_button)
        layout.addWidget(self.result_box)
        layout.addStretch(1)

    def calculate(self) -> None:
        try:
            result = self.service.compute(
                stake_a=float(self.stake_input.text()),
                odds_a=float(self.odds_a_input.text()),
                odds_b=float(self.odds_b_input.text()),
                commission_b=float(self.comm_input.text()),
                mode=self.mode_input.currentText(),
                stake_source=self.source_input.currentText(),
            )
        except Exception as exc:  # pragma: no cover - UI feedback
            self.results_labels["metric"].setText(str(exc))
            return
        self.results_labels["hedge"].setText(f"{result.hedge_stake_b:.2f}")
        self.results_labels["exposure"].setText(f"{result.exposure_b:.2f}")
        self.results_labels["profit_a"].setText(f"{result.profit_a_wins:.2f}")
        self.results_labels["profit_b"].setText(f"{result.profit_b_wins:.2f}")
        metric_value = result.perdida_calificacion or result.beneficio_cnr or 0.0
        self.results_labels["metric"].setText(f"{metric_value:.2f}")
