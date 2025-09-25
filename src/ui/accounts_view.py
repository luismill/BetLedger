"""Accounts view showing balances."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget

from ..services.account_service import AccountService


class AccountsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        layout.addWidget(QLabel("Cuentas disponibles"))
        layout.addWidget(self.list_widget)
        self.service = AccountService()
        self.refresh()

    def refresh(self) -> None:
        self.list_widget.clear()
        for account in self.service.list_accounts():
            self.list_widget.addItem(f"{account.name} — {account.balance:.2f} {account.currency}")
