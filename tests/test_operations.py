from src.domain.models import Account
from src.services.account_service import AccountService
from src.services.operation_service import OperationService


def setup_services(tmp_path, monkeypatch):
    db_path = tmp_path / "test.sqlite"

    def fake_get_db_path():
        return db_path

    monkeypatch.setattr("src.data.db.get_db_path", fake_get_db_path)
    account_service = AccountService()
    origin = account_service.create_account(Account(id=None, name="Origen", type="origen", balance=0.0))
    hedge = account_service.create_account(Account(id=None, name="Exchange", type="contraposicion", commission=5.0, balance=0.0))
    account_service.apply_transaction(account_id=origin.id, kind="deposit", amount=200.0)
    account_service.apply_transaction(account_id=hedge.id, kind="deposit", amount=400.0)
    return account_service, OperationService(account_service)


def test_create_operation_locks_funds(tmp_path, monkeypatch):
    account_service, op_service = setup_services(tmp_path, monkeypatch)
    origin, hedge = account_service.list_accounts()
    operation = op_service.create_operation(
        origin_account_id=origin.id,
        hedge_account_id=hedge.id,
        event="Partido",
        mode="calificacion",
        stake_source="efectivo",
        stake_a=25.0,
        odds_a=2.0,
        odds_b=2.1,
        commission_b=5.0,
    )
    assert operation.status == "PENDIENTE"
    updated_origin = account_service.list_accounts()[0]
    updated_hedge = account_service.list_accounts()[1]
    assert updated_origin.balance < 200.0
    assert updated_hedge.balance < 400.0
