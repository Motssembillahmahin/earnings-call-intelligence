from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

import db

_DB_ROOT = Path(db.__file__).parents[2]  # .../libs/db


def _alembic_config(url: str) -> Config:
    cfg = Config(str(_DB_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_DB_ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def test_initial_migration_creates_model_tables(tmp_path):
    url = f"sqlite:///{tmp_path / 'mig.db'}"
    command.upgrade(_alembic_config(url), "head")

    tables = set(inspect(create_engine(url)).get_table_names())
    assert {
        "company",
        "event",
        "webcast_source",
        "recording",
        "transcript_segment",
    } <= tables
