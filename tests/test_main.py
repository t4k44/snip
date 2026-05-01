from typer.testing import CliRunner
from snip.main import app
from snip import __version__

runner = CliRunner()

def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"snip {__version__}" in result.stdout

def test_callback_help():
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
