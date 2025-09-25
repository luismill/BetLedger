import pytest

from src.domain.models import Account
from src.services.account_service import AccountService
from src.services.operation_service import OperationService


def prepare_operation(tmp_path, monkeypatch):
    db_path = tmp_path / "test.sqlite"

    def fake_get_db_path():
        return db_path

    monkeypatch.setattr("src.data.db.get_db_path", fake_get_db_path)
    account_service = AccountService()
    origin = account_service.create_account(Account(id=None, name="Origen", type="origen", balance=0.0))
    hedge = account_service.create_account(Account(id=None, name="Exchange", type="contraposicion", balance=0.0))
    account_service.apply_transaction(account_id=origin.id, kind="deposit", amount=200.0)
    account_service.apply_transaction(account_id=hedge.id, kind="deposit", amount=400.0)
    op_service = OperationService(account_service)
    operation = op_service.create_operation(
        origin_account_id=origin.id,
        hedge_account_id=hedge.id,
        event="Juego",
        mode="calificacion",
        stake_source="efectivo",
        stake_a=25.0,
        odds_a=2.0,
        odds_b=2.1,
        commission_b=5.0,
    )
    return account_service, op_service, operation


def test_settle_origin_win(tmp_path, monkeypatch):
    account_service, op_service, operation = prepare_operation(tmp_path, monkeypatch)
    settled = op_service.settle_operation(operation.id, "GANA_A")
    assert settled.status == "GANA_A"
    accounts = account_service.list_accounts()
    assert accounts[0].balance > 200.0


def test_settle_hedge_win(tmp_path, monkeypatch):
    account_service, op_service, operation = prepare_operation(tmp_path, monkeypatch)
    settled = op_service.settle_operation(operation.id, "GANA_B")
    assert settled.status == "GANA_B"
    accounts = account_service.list_accounts()
    assert accounts[1].balance > 400.0


def test_cancel_operation(tmp_path, monkeypatch):
    account_service, op_service, operation = prepare_operation(tmp_path, monkeypatch)
    settled = op_service.settle_operation(operation.id, "ANULADA")
    assert settled.status == "ANULADA"
    accounts = account_service.list_accounts()
    assert accounts[0].balance == pytest.approx(200.0, abs=0.5)
