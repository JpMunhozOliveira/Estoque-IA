from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext

from app.db.database import Base, engine


def test_downgrade_e_upgrade_completos():
    cfg = Config("alembic.ini")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")


def test_models_iguais_ao_banco():
    """Se falhar, o diff mostra o que está nos models mas não numa migration (ou vice-versa)."""
    with engine.connect() as conn:
        diffs = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diffs == []