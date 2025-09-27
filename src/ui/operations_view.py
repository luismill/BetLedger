"""Operations management view allowing basic CRUD."""
from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..services.account_service import AccountService
from ..services.operation_service import OperationService


class OperationsView(QWidget):
    """Simple view to create and cancel operations from the main UI."""

    def __init__(self) -> None:
        super().__init__()
        self.service = OperationService()
        self.account_service = AccountService()
        self.account_lookup: dict[int, str] = {}
        self.edit_operation_id: int | None = None

        layout = QVBoxLayout(self)

        self.message_label = QLabel()
        self.message_label.setObjectName("operationsMessage")
        self.message_label.setVisible(False)

        form_group = QGroupBox("Nueva operación")
        form_layout = QFormLayout()

        self.origin_combo = QComboBox()
        self.hedge_combo = QComboBox()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["calificacion", "credito_no_retorno"])
        self.source_combo = QComboBox()
        self.source_combo.addItems(["efectivo", "credito"])

        self.event_input = QLineEdit()
        self.stake_input = QLineEdit("25")
        self.odds_a_input = QLineEdit("2.0")
        self.odds_b_input = QLineEdit("2.1")
        self.comm_input = QLineEdit("5.0")

        form_layout.addRow("Cuenta origen", self.origin_combo)
        form_layout.addRow("Cuenta cobertura", self.hedge_combo)
        form_layout.addRow("Evento", self.event_input)
        form_layout.addRow("Modo", self.mode_combo)
        form_layout.addRow("Origen stake", self.source_combo)
        form_layout.addRow("Stake A", self.stake_input)
        form_layout.addRow("Cuota A", self.odds_a_input)
        form_layout.addRow("Cuota B", self.odds_b_input)
        form_layout.addRow("Comisión B", self.comm_input)

        form_group.setLayout(form_layout)

        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Crear operación")
        self.create_button.clicked.connect(self._create_operation)
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addStretch(1)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Fecha",
                "Evento",
                "Cuenta origen",
                "Cobertura",
                "Stake A",
                "Cobertura B",
                "Estado",
            ]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        table_actions = QHBoxLayout()
        self.edit_button = QPushButton("Editar seleccionada")
        self.edit_button.clicked.connect(self._load_selected_for_edit)
        table_actions.addWidget(self.edit_button)
        self.settle_a_button = QPushButton("Marcar gana A")
        self.settle_a_button.clicked.connect(lambda: self._settle_selected("GANA_A"))
        table_actions.addWidget(self.settle_a_button)
        self.settle_b_button = QPushButton("Marcar gana B")
        self.settle_b_button.clicked.connect(lambda: self._settle_selected("GANA_B"))
        table_actions.addWidget(self.settle_b_button)
        self.delete_button = QPushButton("Eliminar seleccionada")
        self.delete_button.clicked.connect(self._cancel_selected)
        table_actions.addWidget(self.delete_button)
        table_actions.addStretch(1)

        layout.addWidget(form_group)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.message_label)
        layout.addWidget(self.table)
        layout.addLayout(table_actions)
        layout.addStretch(1)

        self._load_accounts()
        self._refresh_table()

    def _load_accounts(self) -> None:
        self.account_lookup.clear()
        self.origin_combo.clear()
        self.hedge_combo.clear()

        accounts = self.account_service.list_accounts()
        for account in accounts:
            if account.id is None:
                continue
            self.account_lookup[account.id] = account.name
            if account.type == "origen":
                self.origin_combo.addItem(account.name, account.id)
            elif account.type == "contraposicion":
                self.hedge_combo.addItem(account.name, account.id)

        if self.origin_combo.count() == 0:
            self.origin_combo.addItem("No hay cuentas de origen", -1)
        if self.hedge_combo.count() == 0:
            self.hedge_combo.addItem("No hay cuentas de cobertura", -1)

    def _create_operation(self) -> None:
        if self.edit_operation_id is not None:
            self._update_operation()
            return
        self._set_message("")
        origin_id = int(self.origin_combo.currentData() or -1)
        hedge_id = int(self.hedge_combo.currentData() or -1)
        if origin_id <= 0 or hedge_id <= 0:
            self._set_message("Debe seleccionar cuentas válidas", error=True)
            return

        try:
            operation = self.service.create_operation(
                origin_account_id=origin_id,
                hedge_account_id=hedge_id,
                event=self.event_input.text() or "Evento",
                mode=self.mode_combo.currentText(),
                stake_source=self.source_combo.currentText(),
                stake_a=float(self.stake_input.text()),
                odds_a=float(self.odds_a_input.text()),
                odds_b=float(self.odds_b_input.text()),
                commission_b=float(self.comm_input.text()),
            )
        except Exception as exc:  # pragma: no cover - UI feedback
            self._set_message(str(exc), error=True)
            return

        self._set_message(f"Operación {operation.id} creada correctamente")
        self._refresh_table()
        self._reset_form()

    def _update_operation(self) -> None:
        if self.edit_operation_id is None:
            return
        self._set_message("")
        origin_id = int(self.origin_combo.currentData() or -1)
        hedge_id = int(self.hedge_combo.currentData() or -1)
        if origin_id <= 0 or hedge_id <= 0:
            self._set_message("Debe seleccionar cuentas válidas", error=True)
            return
        try:
            operation = self.service.update_operation(
                self.edit_operation_id,
                origin_account_id=origin_id,
                hedge_account_id=hedge_id,
                event=self.event_input.text() or "Evento",
                mode=self.mode_combo.currentText(),
                stake_source=self.source_combo.currentText(),
                stake_a=float(self.stake_input.text()),
                odds_a=float(self.odds_a_input.text()),
                odds_b=float(self.odds_b_input.text()),
                commission_b=float(self.comm_input.text()),
                note="Actualizada desde UI",
            )
        except Exception as exc:  # pragma: no cover - UI feedback
            self._set_message(str(exc), error=True)
            return
        self._set_message(f"Operación {operation.id} actualizada")
        self._refresh_table()
        self._reset_form()

    def _cancel_selected(self) -> None:
        self._set_message("")
        selected = self.table.currentRow()
        if selected < 0:
            self._set_message("Seleccione una operación", error=True)
            return
        operation_id_item = self.table.item(selected, 0)
        if not operation_id_item:
            self._set_message("No se pudo identificar la operación", error=True)
            return
        operation_id = int(operation_id_item.text())
        try:
            self.service.cancel_operation(operation_id, note="Cancelada desde UI")
        except Exception as exc:  # pragma: no cover - UI feedback
            self._set_message(str(exc), error=True)
            return
        self._set_message(f"Operación {operation_id} eliminada")
        self._refresh_table()
        self._reset_form()

    def _load_selected_for_edit(self) -> None:
        self._set_message("")
        selected = self.table.currentRow()
        if selected < 0:
            self._set_message("Seleccione una operación", error=True)
            return
        operation_id_item = self.table.item(selected, 0)
        if not operation_id_item:
            self._set_message("No se pudo identificar la operación", error=True)
            return
        operation_id = int(operation_id_item.text())
        try:
            operation = self.service.get_operation(operation_id)
        except Exception as exc:  # pragma: no cover - UI feedback
            self._set_message(str(exc), error=True)
            return
        if operation.status != "PENDIENTE":
            self._set_message("Solo se pueden editar operaciones pendientes", error=True)
            return
        self._ensure_combo_selection(self.origin_combo, operation.origin_account_id)
        self._ensure_combo_selection(self.hedge_combo, operation.hedge_account_id)
        self.event_input.setText(operation.event)
        self.mode_combo.setCurrentText(operation.mode)
        self.source_combo.setCurrentText(operation.stake_source)
        self.stake_input.setText(f"{operation.stake_a:.2f}")
        self.odds_a_input.setText(f"{operation.odds_a:.2f}")
        self.odds_b_input.setText(f"{operation.odds_b:.2f}")
        self.comm_input.setText(f"{operation.commission_b:.2f}")
        self.edit_operation_id = operation.id
        self.create_button.setText("Guardar cambios")
        self._set_message(f"Editando operación {operation.id}")

    def _settle_selected(self, outcome: str) -> None:
        self._set_message("")
        selected = self.table.currentRow()
        if selected < 0:
            self._set_message("Seleccione una operación", error=True)
            return
        operation_id_item = self.table.item(selected, 0)
        if not operation_id_item:
            self._set_message("No se pudo identificar la operación", error=True)
            return
        operation_id = int(operation_id_item.text())
        try:
            operation = self.service.settle_operation(operation_id, outcome, note="Resultado registrado desde UI")
        except Exception as exc:  # pragma: no cover - UI feedback
            self._set_message(str(exc), error=True)
            return
        self._set_message(f"Resultado registrado para la operación {operation.id}")
        self._refresh_table()
        self._reset_form()

    def _refresh_table(self) -> None:
        operations = [op for op in self.service.list_operations(include_cancelled=False)]
        self.table.setRowCount(len(operations))
        for row, operation in enumerate(operations):
            self.table.setItem(row, 0, QTableWidgetItem(str(operation.id)))
            self.table.setItem(row, 1, QTableWidgetItem(self._format_ts(operation.ts)))
            self.table.setItem(row, 2, QTableWidgetItem(operation.event))
            self.table.setItem(row, 3, QTableWidgetItem(self.account_lookup.get(operation.origin_account_id, "")))
            self.table.setItem(row, 4, QTableWidgetItem(self.account_lookup.get(operation.hedge_account_id, "")))
            self.table.setItem(row, 5, QTableWidgetItem(f"{operation.stake_a:.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{operation.hedge_stake_b:.2f}"))
            self.table.setItem(row, 7, QTableWidgetItem(operation.status))
        self.table.resizeColumnsToContents()
        if self.edit_operation_id is not None:
            self.create_button.setText("Guardar cambios")
        else:
            self.create_button.setText("Crear operación")

    def _set_message(self, text: str, *, error: bool = False) -> None:
        if text:
            self.message_label.setText(text)
            self.message_label.setStyleSheet("color: red;" if error else "color: green;")
            self.message_label.setVisible(True)
        else:
            self.message_label.clear()
            self.message_label.setVisible(False)

    def _reset_form(self) -> None:
        self.edit_operation_id = None
        self.create_button.setText("Crear operación")

    def _ensure_combo_selection(self, combo: QComboBox, value: int) -> None:
        index = combo.findData(value)
        if index == -1:
            name = self.account_lookup.get(value, str(value))
            combo.addItem(name, value)
            index = combo.count() - 1
        combo.setCurrentIndex(index)

    @staticmethod
    def _format_ts(ts: datetime) -> str:
        return ts.strftime("%Y-%m-%d %H:%M")
