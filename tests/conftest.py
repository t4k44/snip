import pytest
import sqlite_utils
from contextlib import contextmanager
from snip import constants as C
import snip.utils

@pytest.fixture
def db():
    """In-memory database fixture."""
    _db = sqlite_utils.Database(":memory:")
    yield _db
    _db.conn.close()

@pytest.fixture(autouse=True)
def mock_get_db(mocker, db):
    """Mock get_db to return the in-memory database."""
    @contextmanager
    def _mocked_get_db():
        yield db

    # Patch in all modules that use get_db
    mocker.patch("snip.utils.get_db", side_effect=_mocked_get_db)
    mocker.patch("snip.snippets.get_db", side_effect=_mocked_get_db)
    mocker.patch("snip.list.get_db", side_effect=_mocked_get_db)
    mocker.patch("snip.tui.get_db", side_effect=_mocked_get_db)
    mocker.patch("snip.gui.get_db", side_effect=_mocked_get_db)
    return _mocked_get_db

@pytest.fixture(autouse=True)
def mock_stdin(mocker):
    """
    Mock sys.stdin.isatty to return True.
    Note: CliRunner often replaces stdin, so tests requiring specific stdin
    behavior should use the 'input' parameter in runner.invoke().
    """
    mocker.patch("sys.stdin.isatty", return_value=True)

@pytest.fixture
def init_db(db):
    """Initialize the database table with all columns."""
    columns = {field: str for field in C.TARGET_FIELD}
    columns["abbr"] = int
    columns["rate"] = int
    # tags will be stored as JSON (TEXT in sqlite)
    db[C.TABLE].create(columns, pk="id")
    return db

@pytest.fixture(autouse=True)
def mock_paths(monkeypatch, tmp_path):
    """Mock file paths to use a temporary directory."""
    fish_abbr = tmp_path / "abbr.fish"
    monkeypatch.setattr(C, "FISH_ABBR", fish_abbr)
    return {"fish_abbr": fish_abbr}
