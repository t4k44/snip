import subprocess

import typer
from pyutils.logger import setup_logger

import snip.constants as C
from snip.utils import body_remove_input_place, get_db

app = typer.Typer(help="gui")
logging = setup_logger(__name__)

@app.command()
def pop(tag: str = typer.Argument("name")):
    """rofi等のGUIを起動する"""

    query  = f"""
        SELECT
            id, trigger, tags,
            replace(substr(body, 0, {C.ROFI_STRLEN}), char(10), '⏎ ') AS body,
            replace(substr(memo, 0, {C.ROFI_STRLEN}), char(10), '⏎ ') AS memo
        FROM snippets
        WHERE EXISTS (SELECT 1 FROM json_each(snippets.tags) WHERE value = ?)
        ORDER BY rate DESC, id DESC
    """

    with get_db() as db:
        rows = db.query(query, [tag])
        rows = [f"{row['trigger']}\t / \t{row['body']}"
                f"\t{row['memo']}\t{row['tags']}\t{int(row['id']):04d}" for row in rows]

        try:
            choice = subprocess.run(C.ROFI, input="\n".join(rows), stdout=subprocess.PIPE, text=True)
            if choice.returncode != 0: return

            target = db[C.TABLE].get(choice.stdout.split()[-1])

            db[C.TABLE].update(target["id"], {"rate": target["rate"] + 1})

            body = body_remove_input_place(target)
            logging.debug(body)

            subprocess.run(C.CLIP_COPY_CMD + [body], check=True)
            subprocess.run(C.CLIP_PASTE_CMD, check=True)
            logging.debug("DONE")

        except subprocess.CalledProcessError as e:
            logging.error("stdout: %s", e.stdout)
            logging.error("stderr: %s", e.stderr)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    サブコマンドが指定されていない場合に実行される処理
    """
    if ctx.invoked_subcommand is None:
        pop(tag="name")
