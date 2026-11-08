from typer.testing import CliRunner

import snip.constants as C
from snip.main import app
from snip.models import AbbrFlag

runner = CliRunner()

def test_fish_abbr_output(init_db, mock_paths):
    db = init_db
    # Insert a snippet with abbr flag
    db[C.TABLE].insert({
        "trigger": "g",
        "body": "git status",
        "abbr": AbbrFlag.SIMPLE.value,
        "tags": ["git"],
        "memo": "",
        "mode": None,
        "fish_cur_mark": None
    }, pk="id")

    # Another one with position anywhere
    db[C.TABLE].insert({
        "trigger": "L",
        "body": "| less",
        "abbr": (AbbrFlag.SIMPLE | AbbrFlag.POSITION_ANYWHERE).value,
        "tags": ["sh"],
        "memo": "",
        "mode": None,
        "fish_cur_mark": None
    }, pk="id")

    result = runner.invoke(app, ["list", "fish"])
    assert result.exit_code == 0

    fish_abbr_file = mock_paths["fish_abbr"]
    assert fish_abbr_file.exists()

    content = fish_abbr_file.read_text()
    assert "abbr --add -- g 'git status'" in content
    assert "abbr --add --position anywhere -- L '| less'" in content
    assert content.endswith("\n")

def test_fish_abbr_with_cursor(init_db, mock_paths):
    db = init_db
    db[C.TABLE].insert({
        "trigger": "gcd",
        "body": "git commit -m '%%'",
        "abbr": (AbbrFlag.SIMPLE | AbbrFlag.SET_CURSOR).value,
        "fish_cur_mark": "%%",
        "tags": ["git"],
        "memo": "",
        "mode": None
    }, pk="id")

    db[C.TABLE].insert({
        "trigger": "gc",
        "body": "git commit -m '%'",
        "abbr": (AbbrFlag.SIMPLE | AbbrFlag.SET_CURSOR).value,
        "fish_cur_mark": None,
        "tags": ["git"],
        "memo": "",
        "mode": None
    }, pk="id")

    result = runner.invoke(app, ["list", "fish"])
    assert result.exit_code == 0

    content = mock_paths["fish_abbr"].read_text()
    # Note: shlex.quote will handle '%' appropriately
    assert "abbr --add --set-cursor=%% -- gcd 'git commit -m '" in content
    assert "abbr --add --set-cursor -- gc 'git commit -m '"     in content

def test_cheat_sheet(init_db):
    db = init_db
    db[C.TABLE].insert({
        "trigger": "test_trigger",
        "body": "test_body",
        "tags": ["test_tag"],
        "memo": "test_memo",
        "abbr": 0,
        "mode": None,
        "fish_cur_mark": None
    }, pk="id")

    result = runner.invoke(app, ["list", "cs", "test_tag"])
    assert result.exit_code == 0
    assert "test_trigger" in result.stdout
    assert "test_body" in result.stdout
    assert "test_memo" in result.stdout

def test_cheat_sheet_does_not_interpret_markup(init_db):
    init_db[C.TABLE].insert({"trigger": "t", "body": "echo [bold]x[/bold]", "tags": ["m"]}, pk="id")
    result = runner.invoke(app, ["list", "cs", "m"])
    assert result.exit_code == 0
    assert "[bold]x[/bold]" in result.stdout

def test_fish_abbr_empty(init_db):
    result = runner.invoke(app, ["list", "fish"])
    assert result.exit_code == 0
    assert "登録対象なし" in result.stdout

def test_skk_output(init_db, mock_paths):
    init_db[C.TABLE].insert({"trigger": "mail", "body": "a@b.c%", "tags": ["skk"]}, pk="id")
    result = runner.invoke(app, ["list", "skk"])
    assert result.exit_code == 0
    assert "mail /a@b.c/" in mock_paths["skk_abbr"].read_text()

def test_nvim_t_mode_multiline_and_escape(init_db, mock_paths):
    init_db[C.TABLE].insert({"trigger": "mt", "body": 'a\nb"c', "tags": ["text"], "mode": "t"}, pk="id")
    result = runner.invoke(app, ["list", "nvim"])
    assert result.exit_code == 0

    content = (mock_paths["nvim_snip"] / "text.lua").read_text()
    assert 's("mt", t({"a", "b\\"c"}))' in content

def test_nvim_fmta_nodes_are_unique(init_db, mock_paths):
    init_db[C.TABLE].insert({"trigger": "mf", "body": "x <1> <1> <2>", "tags": ["python"], "mode": "fmta"}, pk="id")
    result = runner.invoke(app, ["list", "nvim"])
    assert result.exit_code == 0

    content = (mock_paths["nvim_snip"] / "python.lua").read_text()
    assert "{ i(1), i(2) }" in content
    assert content.count("i(1)") == 1
