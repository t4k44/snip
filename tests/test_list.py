from typer.testing import CliRunner
from snip.main import app
import snip.constants as C
from snip.utils import AbbrFlag

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

def test_fish_abbr_with_cursor(init_db, mock_paths):
    db = init_db
    db[C.TABLE].insert({
        "trigger": "gc",
        "body": "git commit -m '%'",
        "abbr": (AbbrFlag.SIMPLE | AbbrFlag.SET_CURSOR).value,
        "fish_cur_mark": "%",
        "tags": ["git"],
        "memo": "",
        "mode": None
    }, pk="id")
    
    result = runner.invoke(app, ["list", "fish"])
    assert result.exit_code == 0
    
    content = mock_paths["fish_abbr"].read_text()
    # Note: shlex.quote will handle '%' appropriately
    assert "abbr --add --set-cursor=% -- gc 'git commit -m '" in content

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

def test_fish_abbr_empty(init_db):
    result = runner.invoke(app, ["list", "fish"])
    assert result.exit_code == 0
    assert "登録対象なし" in result.stdout
