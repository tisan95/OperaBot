"""Root test configuration.

Sets the test DATABASE_URL *before* any app module is imported so that
app.config.Settings picks up SQLite instead of the dev PostgreSQL URL.
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./tests/test.db")
os.environ.setdefault("DEBUG", "False")
