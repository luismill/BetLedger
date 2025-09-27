from src.domain.models import Account
from src.services.account_service import AccountService


def test_create_account_and_transaction(tmp_path, monkeypatch):
    db_path = tmp_path / "test.sqlite"

    def fake_get_db_path():
        return db_path

    monkeypatch.setattr("src.data.db.get_db_path", fake_get_db_path)
    service = AccountService()

    account = service.create_account(
        Account(id=None, name="Test", owner="Alice", type="origen", balance=0.0)
    )
    assert account.id is not None

    service.apply_transaction(account_id=account.id, kind="deposit", amount=100.0)
    service.apply_transaction(account_id=account.id, kind="incentive", amount=25.0)
    accounts = service.list_accounts()
    assert accounts[0].balance == 100.0
    assert accounts[0].bonus_balance == 25.0

    assert service.reconcile_account(account.id)
