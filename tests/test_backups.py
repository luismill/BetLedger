from pathlib import Path

from src.data import backups, db


def test_backup_creation(tmp_path, monkeypatch):
    db_path = tmp_path / "db.sqlite"

    def fake_get_db_path():
        return db_path

    monkeypatch.setattr("src.data.db.get_db_path", fake_get_db_path)
    monkeypatch.setattr("src.data.backups.get_db_path", fake_get_db_path)
    db.initialise_database()
    db_path.write_text("test")

    monkeypatch.setattr("src.data.backups.BACKUP_DIR", tmp_path)
    backup_file = backups.create_backup()
    assert backup_file.exists()
