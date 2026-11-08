import json

from typer.testing import CliRunner

import snip.constants as C
from snip.main import app

runner = CliRunner()

def _insert(db, **kw):
    row = {"trigger": "t", "body": "b", "memo": "m", "abbr": 0, "tags": ["x"]}
    row.update(kw)
    db[C.TABLE].insert(row, pk="id")
    return list(db[C.TABLE].rows)[-1]["id"]

def test_add_snippet_from_stdin(init_db):
    db = init_db
    # body 引数が無いときだけ stdin から読む
    result = runner.invoke(app, ["add", "hello", "--tags", "test"], input="echo hello")
    assert result.exit_code == 0
    assert "DONE" in result.stdout

    rows = list(db[C.TABLE].rows)
    assert len(rows) == 1
    assert rows[0]["trigger"] == "hello"
    assert rows[0]["body"] == "echo hello"
    assert json.loads(rows[0]["tags"]) == ["test"]

def test_add_snippet_body_arg_wins_over_stdin(init_db):
    db = init_db
    result = runner.invoke(app, ["add", "hi", "echo", "hi", "-t", "a,b"], input="ignored")
    assert result.exit_code == 0

    row = list(db[C.TABLE].rows)[0]
    assert row["body"] == "echo hi"
    assert json.loads(row["tags"]) == ["a", "b"]
    assert row["rate"] == 0

def test_add_snippet_abbr_flags(init_db):
    db = init_db
    result = runner.invoke(app, ["add", "g", "git", "-p", "-c"])
    assert result.exit_code == 0
    assert list(db[C.TABLE].rows)[0]["abbr"] == 7  # SIMPLE | POSITION | CURSOR

def test_edit_snippet(init_db):
    db = init_db
    row_id = _insert(db, trigger="old", body="old body", tags=["old"], memo="")

    result = runner.invoke(app, ["edit", str(row_id), "--trigger", "new", "--body", "new body"])
    assert result.exit_code == 0
    assert "UPDATE" in result.stdout

    row = db[C.TABLE].get(row_id)
    assert row["trigger"] == "new"
    assert row["body"] == "new body"

def test_edit_body_from_stdin_dash(init_db):
    db = init_db
    row_id = _insert(db)
    result = runner.invoke(app, ["edit", str(row_id), "--body", "-"], input="piped body\n")
    assert result.exit_code == 0
    assert db[C.TABLE].get(row_id)["body"] == "piped body"

def test_edit_does_not_read_stdin_implicitly(init_db):
    db = init_db
    row_id = _insert(db, body="keep")
    result = runner.invoke(app, ["edit", str(row_id), "--memo", "new"], input="should not be used")
    assert result.exit_code == 0

    row = db[C.TABLE].get(row_id)
    assert row["body"] == "keep"
    assert row["memo"] == "new"

def test_edit_can_clear_memo(init_db):
    db = init_db
    row_id = _insert(db, memo="something")
    result = runner.invoke(app, ["edit", str(row_id), "--memo", ""])
    assert result.exit_code == 0
    assert db[C.TABLE].get(row_id)["memo"] == ""

def test_edit_without_flags_keeps_abbr(init_db):
    db = init_db
    row_id = _insert(db, abbr=5)
    result = runner.invoke(app, ["edit", str(row_id), "--memo", "y"])
    assert result.exit_code == 0
    assert db[C.TABLE].get(row_id)["abbr"] == 5

def test_edit_can_reset_abbr(init_db):
    db = init_db
    row_id = _insert(db, abbr=5)
    result = runner.invoke(app, ["edit", str(row_id), "--no-abbr", "--no-position", "--no-cursor"])
    assert result.exit_code == 0
    assert db[C.TABLE].get(row_id)["abbr"] == 0

def test_edit_missing_id(init_db):
    result = runner.invoke(app, ["edit", "999", "--memo", "x"])
    assert result.exit_code == 1
    assert init_db[C.TABLE].count == 0

def test_delete_snippet(init_db):
    db = init_db
    row_id = _insert(db, trigger="to_delete", body="content")

    result = runner.invoke(app, ["delete", str(row_id)])
    assert result.exit_code == 0
    assert "DELETED" in result.stdout

    assert db[C.TABLE].count == 0

def test_delete_missing_id(init_db):
    result = runner.invoke(app, ["delete", "999"])
    assert result.exit_code == 1
