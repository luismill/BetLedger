"""Accounts view with management tools for balances and bonuses."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..domain.models import Account
from ..services.account_service import AccountService


class AccountsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service = AccountService()
        self.accounts: list[Account] = []

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Cuentas disponibles"))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        layout.addWidget(self._build_creation_group())
        layout.addWidget(self._build_transaction_group())

        self.refresh()

    def _build_creation_group(self) -> QGroupBox:
        group = QGroupBox("Crear cuenta")
        form = QFormLayout(group)

        self.name_input = QLineEdit()
        self.owner_input = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["origen", "contraposicion"])
        self.currency_input = QLineEdit("EUR")

        form.addRow("Nombre", self.name_input)
        form.addRow("Persona", self.owner_input)
        form.addRow("Tipo", self.type_combo)
        form.addRow("Divisa", self.currency_input)

        button = QPushButton("Crear cuenta")
        button.clicked.connect(self._handle_create_account)
        form.addRow(button)
        return group

    def _build_transaction_group(self) -> QGroupBox:
        group = QGroupBox("Registrar movimiento")
        form = QFormLayout(group)

        self.account_combo = QComboBox()
        self.account_combo.currentIndexChanged.connect(self._update_amount_prefix)
        self.movement_combo = QComboBox()
        self.movement_combo.addItem("Depósito", userData="deposit")
        self.movement_combo.addItem("Bono recibido", userData="incentive")
        self.movement_combo.addItem("Retirada", userData="withdrawal")

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.0, 1_000_000.0)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("€ ")

        self.note_input = QLineEdit()

        form.addRow("Cuenta", self.account_combo)
        form.addRow("Movimiento", self.movement_combo)
        form.addRow("Importe", self.amount_input)
        form.addRow("Nota", self.note_input)

        button = QPushButton("Registrar")
        button.clicked.connect(self._handle_transaction)
        form.addRow(button)
        return group

    def refresh(self) -> None:
        self.accounts = self.service.list_accounts()
        self.list_widget.clear()
        self.account_combo.blockSignals(True)
        self.account_combo.clear()
        for account in self.accounts:
            display = (
                f"{account.name} ({account.owner}) — "
                f"Saldo: {account.balance:.2f} {account.currency} | "
                f"Bono: {account.bonus_balance:.2f} {account.currency}"
            )
            self.list_widget.addItem(display)
            self.account_combo.addItem(display, userData=account.id)
        self.account_combo.blockSignals(False)
        self._update_amount_prefix()

    def _handle_create_account(self) -> None:
        name = self.name_input.text().strip()
        owner = self.owner_input.text().strip()
        currency = self.currency_input.text().strip().upper() or "EUR"
        if not name or not owner:
            QMessageBox.warning(self, "Datos incompletos", "Nombre y persona son obligatorios.")
            return

        account = Account(
            id=None,
            name=name,
            owner=owner,
            type=self.type_combo.currentText(),
            currency=currency,
        )
        try:
            self.service.create_account(account)
        except Exception as exc:  # pragma: no cover - UI feedback
            QMessageBox.critical(self, "Error", str(exc))
            return

        self.name_input.clear()
        self.owner_input.clear()
        self.currency_input.setText(currency)
        self.refresh()

    def _handle_transaction(self) -> None:
        if not self.accounts:
            QMessageBox.information(self, "Sin cuentas", "Primero crea una cuenta.")
            return

        account_id = self.account_combo.currentData()
        if account_id is None:
            QMessageBox.warning(self, "Selección inválida", "Selecciona una cuenta válida.")
            return

        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "Importe inválido", "Introduce un importe positivo.")
            return

        kind = self.movement_combo.currentData()
        adjusted_amount = -amount if kind == "withdrawal" else amount
        note = self.note_input.text().strip() or None

        try:
            self.service.apply_transaction(
                account_id=account_id,
                kind=kind,
                amount=adjusted_amount,
                note=note,
            )
        except Exception as exc:  # pragma: no cover - UI feedback
            QMessageBox.critical(self, "Error", str(exc))
            return

        self.amount_input.setValue(0.0)
        self.note_input.clear()
        self.refresh()

    def _update_amount_prefix(self) -> None:
        if 0 <= self.account_combo.currentIndex() < len(self.accounts):
            currency = self.accounts[self.account_combo.currentIndex()].currency
            self.amount_input.setPrefix(f"{currency} ")
        else:
            self.amount_input.setPrefix("€ ")
