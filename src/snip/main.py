
import typer
from pyutils.logger import setup_logger

import snip.constants as C
from snip import __version__
from snip.gui import app as gui_app  # 別ファイルのTyper
from snip.list import app as list_app
from snip.snippets import app as snip_app
from snip.tui import app as tui_app

APP_NAME = "snip"
logger   = setup_logger(__name__)
app      = typer.Typer(help="snippet管理tool",
                       context_settings={"help_option_names": ["-h", "--help"]})

app.add_typer(snip_app)
app.add_typer(tui_app,  name="tui")
app.add_typer(gui_app,  name="gui")
app.add_typer(list_app, name="list")
app.add_typer(list_app, name="l", hidden=True)


def version_callback(value: bool):
    if value:
        print(f"{APP_NAME} {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context,
             version: bool | None = typer.Option(None, "--version", "-v", callback=version_callback,
                                                 is_eager=True, help="Display version information")
):
    """
    コマンドが指定されていない場合に実行
    """
    logger.debug(f"subcommand: {ctx.invoked_subcommand}")
    C.DB_PATH.mkdir(parents=True, exist_ok=True)
    if ctx.invoked_subcommand is None:
        ctx.get_help()
        raise typer.Exit()


def main(): app()
if __name__ == "__main__": main()
