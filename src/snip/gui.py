import subprocess

import typer
from pyutils.logger import setup_logger

import snip.constants as C
from snip.utils import body_remove_input_place, find_row, get_db

app = typer.Typer(help="Rofi等を起動し、スニペットを選択＆ペースト")
logger = setup_logger(__name__)


@app.command()
def pop(tag: str = typer.Argument("name")):
    """rofi等のGUIを起動する"""

    query = f"""
        SELECT
            id, trigger, tags,
            replace(substr(body, 1, ?), char(10), '⏎ ') AS body,
            replace(substr(memo, 1, ?), char(10), '⏎ ') AS memo
        FROM {C.TABLE}
        WHERE {C.TAG_FILTER}
        ORDER BY rate DESC, id DESC
    """

    with get_db() as db:
        rows = db.query(query, [C.ROFI_STRLEN, C.ROFI_STRLEN, tag])
        rows = [f"{row['trigger']}\t / \t{row['body']}"
                f"\t{row['memo']}\t{row['tags']}\t{int(row['id']):04d}" for row in rows]

        try:
            choice = subprocess.run(C.ROFI, input="\n".join(rows), stdout=subprocess.PIPE, text=True)
            if choice.returncode != 0: return

            fields = choice.stdout.split()
            if not fields: return
            try:
                row_id = int(fields[-1])
            except ValueError:
                logger.error("invalid rofi output: %s", choice.stdout)
                return

            target = find_row(db, row_id)
            if target is None: return

            db[C.TABLE].update(target["id"], {"rate": (target.get("rate") or 0) + 1})

            body = body_remove_input_place(target)
            logger.debug(body)

            subprocess.run(C.CLIP_COPY_CMD + [body], check=True)
            subprocess.run(C.CLIP_PASTE_CMD, check=True)
            logger.debug("DONE")

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error("command failed: %s", e)
            raise typer.Exit(code=1) from e


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    サブコマンドが指定されていない場合に実行される処理
    """
    if ctx.invoked_subcommand is None:
        pop(tag="name")
