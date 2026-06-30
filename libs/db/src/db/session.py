"""Engine and session helpers built from ``common.Settings``."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session


def get_engine(url: str | None = None) -> Engine:
    """Create an engine for ``url`` (defaults to ``Settings.database_url``)."""
    from common import get_settings

    return create_engine(url or get_settings().database_url)


@contextmanager
def session_scope(engine: Engine) -> Iterator[Session]:
    """Transactional session: commit on success, roll back on exception."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
