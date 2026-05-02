from typer.testing import CliRunner

import snip.constants as C
from snip.main import app

runner = CliRunner()

def test_tui_raw(init_db):
    db = init_db
    db[C.TABLE].insert({
        "trigger": "t1",
        "body": "b1",
        "tags": ["test"],
        "abbr": 0,
        "rate": 10,
        "memo": "m1",
        "mode": None,
        "fish_cur_mark": None
    }, pk="id")

    result = runner.invoke(app, ["tui", "list", "test"])
    assert result.exit_code == 0
    assert "t1" in result.stdout
    assert "b1" in result.stdout

def test_tui_preview(init_db):
    db = init_db
    db[C.TABLE].insert({
        "trigger": "t1",
        "body": "body_content",
        "tags": ["test"],
        "abbr": 0,
        "memo": "memo_content",
        "rate": 0,
        "mode": None,
        "fish_cur_mark": None
    }, pk="id")
    row_id = list(db[C.TABLE].rows)[0]["id"]

    result = runner.invoke(app, ["tui", "preview", str(row_id)])
    assert result.exit_code == 0
    assert "body_content" in result.stdout
    assert "---" in result.stdout
    assert "memo_content" in result.stdout

def test_tui_get(init_db):
    db = init_db
    db[C.TABLE].insert({
        "trigger": "t1",
        "body": "get_this",
        "tags": ["test"],
        "abbr": 0,
        "rate": 5,
        "memo": "",
        "mode": None,
        "fish_cur_mark": None
    }, pk="id")
    row_id = list(db[C.TABLE].rows)[0]["id"]

    result = runner.invoke(app, ["tui", "get", str(row_id)])
    assert result.exit_code == 0
    assert "get_this" in result.stdout

    # Check rate incremented
    row = db[C.TABLE].get(row_id)
    assert row["rate"] == 6
