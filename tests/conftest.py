from contextlib import contextmanager

import pytest
import sqlite_utils

from snip import constants as C
from snip.utils import ensure_schema


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
    mocker.patch("snip.editor.get_db", side_effect=_mocked_get_db)
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
    """Initialize the database with the real (production) schema."""
    ensure_schema(db)
    return db

@pytest.fixture(autouse=True)
def mock_paths(monkeypatch, tmp_path):
    """Mock file paths to use a temporary directory."""
    paths = {
        "fish_abbr": tmp_path / "fish" / "abbr.fish",
        "nvim_snip": tmp_path / "nvim" / "luasnippets",
        "skk_abbr":  tmp_path / "skk" / "abbr.dict",
    }
    monkeypatch.setattr(C, "FISH_ABBR", paths["fish_abbr"])
    monkeypatch.setattr(C, "NVIM_SNIP", paths["nvim_snip"])
    monkeypatch.setattr(C, "SKK_ABBR",  paths["skk_abbr"])
    return paths
