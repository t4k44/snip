import subprocess
from typer.testing import CliRunner
from snip.main import app
import snip.constants as C

runner = CliRunner()

def test_gui_pop(init_db, mocker):
    db = init_db
    db[C.TABLE].insert({
        "trigger": "g1",
        "body": "body1",
        "tags": ["gui"],
        "rate": 0,
        "memo": "",
        "abbr": 0,
        "mode": None,
        "fish_cur_mark": None
    }, pk="id")
    row_id = list(db[C.TABLE].rows)[0]["id"]
    
    # Mock subprocess.run for rofi choice
    # rofi output should contain the ID at the end
    mock_rofi = mocker.Mock()
    mock_rofi.returncode = 0
    mock_rofi.stdout = f"g1\t / \tbody1\t\t['gui']\t{row_id:04d}"
    
    mock_run = mocker.patch("subprocess.run", return_value=mock_rofi)
    
    result = runner.invoke(app, ["gui", "pop", "gui"])
    assert result.exit_code == 0
    
    # Check rate incremented
    row = db[C.TABLE].get(row_id)
    assert row["rate"] == 1
    
    # Verify clipboard commands called
    # C.CLIP_COPY_CMD + [body], C.CLIP_PASTE_CMD
    calls = [call.args[0] for call in mock_run.call_args_list]
    assert any(C.CLIP_COPY_CMD[0] in cmd for cmd in calls)
    assert any(C.CLIP_PASTE_CMD[0] in cmd for cmd in calls)
