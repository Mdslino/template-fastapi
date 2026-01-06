from sqlalchemy import text


def test_database_connection(db):
    """Test that database connection is working."""
    result = db.execute(text('SELECT 1'))
    assert result.scalar() == 1


def test_database_version(db):
    """Test PostgreSQL version."""
    result = db.execute(text('SELECT version()'))
    version = result.scalar()
    assert version is not None
    assert 'PostgreSQL' in version


def test_uuid_extension_enabled(db):
    """Test that uuid-ossp extension is enabled."""
    result = db.execute(
        text("SELECT COUNT(*) FROM pg_extension WHERE extname = 'uuid-ossp'")
    )
    assert result.scalar() == 1


def test_database_write_and_read(db):
    """Test basic database write and read operations."""
    # Create a temporary table
    db.execute(
        text(
            """
            CREATE TEMPORARY TABLE test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100)
            )
        """
        )
    )
    db.commit()

    # Insert data
    db.execute(text("INSERT INTO test_table (name) VALUES ('test_value')"))
    db.commit()

    # Read data
    result = db.execute(text('SELECT name FROM test_table'))
    name = result.scalar()

    assert name == 'test_value'


def test_database_transaction_rollback(db):
    """Test that database transactions can be rolled back."""
    # Create a temporary table
    db.execute(
        text(
            """
            CREATE TEMPORARY TABLE test_rollback (
                id SERIAL PRIMARY KEY,
                value VARCHAR(50)
            )
        """
        )
    )
    db.commit()

    # Insert and rollback
    db.execute(text("INSERT INTO test_rollback (value) VALUES ('test')"))
    db.rollback()

    # Verify rollback worked
    result = db.execute(text('SELECT COUNT(*) FROM test_rollback'))
    assert result.scalar() == 0

    # Insert and commit
    db.execute(text("INSERT INTO test_rollback (value) VALUES ('committed')"))
    db.commit()

    # Verify commit worked
    result = db.execute(text('SELECT COUNT(*) FROM test_rollback'))
    assert result.scalar() == 1
