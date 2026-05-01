import json

from typer.testing import CliRunner

import snip.constants as C
from snip.main import app

runner = CliRunner()

def test_add_snippet(init_db):
    db = init_db
    # Since CliRunner's stdin is not a TTY, we provide body via input (stdin)
    # and provide a dummy argument for the required body parameter.
    result = runner.invoke(app, ["add", "hello", "dummy", "--tags", "test"], input="echo hello")
    assert result.exit_code == 0
    assert "DONE" in result.stdout

    rows = list(db[C.TABLE].rows)
    assert len(rows) == 1
    assert rows[0]["trigger"] == "hello"
    assert rows[0]["body"] == "echo hello"
    assert json.loads(rows[0]["tags"]) == ["test"]

def test_edit_snippet(init_db):
    db = init_db
    # Prepare data
    db[C.TABLE].insert({
        "trigger": "old",
        "body": "old body",
        "tags": ["old"],
        "abbr": 0,
        "memo": "",
        "mode": None,
        "fish_cur_mark": None
    }, pk="id")
    row_id = list(db[C.TABLE].rows)[0]["id"]

    # Similarly, provide new body via stdin
    result = runner.invoke(app, ["edit", str(row_id), "--trigger", "new"], input="new body")
    assert result.exit_code == 0
    assert "UPDATE" in result.stdout

    row = db[C.TABLE].get(row_id)
    assert row["trigger"] == "new"
    assert row["body"] == "new body"

def test_delete_snippet(init_db):
    db = init_db
    db[C.TABLE].insert({"trigger": "to_delete", "body": "content"}, pk="id")
    row_id = list(db[C.TABLE].rows)[0]["id"]

    result = runner.invoke(app, ["delete", str(row_id)])
    assert result.exit_code == 0
    assert "DELETED" in result.stdout

    assert db[C.TABLE].count == 0
