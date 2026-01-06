"""
This module is kept for backwards compatibility.
Database session and engine are now managed via Testcontainers in conftest.py.

Import the Session and engine fixtures directly from conftest.py instead:
    from conftest import Session, engine
"""

# These are placeholder imports - use fixtures from conftest.py in tests
Session = None
engine = None
