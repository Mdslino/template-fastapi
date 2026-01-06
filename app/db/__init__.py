from sqlalchemy import Engine, create_engine

_engine: Engine | None = None


def get_engine() -> Engine:
    """Get or create the database engine (lazy initialization)."""
    global _engine
    if _engine is None:
        from core.config import get_settings

        settings = get_settings()
        _engine = create_engine(
            settings.SQLALCHEMY_DATABASE_URI.unicode_string(),
            pool_pre_ping=True,  # type: ignore
        )
    return _engine


# Backward compatibility - call get_engine() when accessed
def __getattr__(name: str):
    """Lazy attribute access for backward compatibility."""
    if name == 'engine':
        return get_engine()
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
