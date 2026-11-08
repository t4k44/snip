import json

import typer
from pyutils.logger import setup_logger

import snip.constants as C
from snip.utils import body_remove_input_place, find_row, get_db

app = typer.Typer(help="tui用低レベルコマンド")
logger = setup_logger(__name__)


@app.command("list")
def list_snippets(tag: str = typer.Argument("fish")):
    """fzfに渡すためのタブ区切り一覧を出力"""
    lines = []

    with get_db() as db:
        logger.debug(f"tag: {tag}")
        for row in db[C.TABLE].rows_where(C.TAG_FILTER, [tag], order_by="rate DESC, id DESC"):
            body = "⏎ ".join(body_remove_input_place(row).splitlines())
            tags = json.loads(row["tags"] or "[]")
            lngm = (tags[0] if tags and tags[0] != "name" else "txt")
            lngm = "vim" if lngm == "nvim" else lngm

            lines.append(f'{row["id"]}\t{row["trigger"]}\t{body}\t[tags: {",".join(tags)}]\t{lngm}')

    print("\n".join(lines))


@app.command()
def preview(id: int):
    """指定IDのスニペットのプレビューを表示"""
    logger.debug(f"id: {id}")
    with get_db() as db:
        row = find_row(db, id)
        if row is None:
            return

        body  = body_remove_input_place(row)
        body += "\n---\n"
        body += row.get("memo") or ""
        body += "\n---\n"
        body += f"{row.get('tags') or ''} (id: {row.get('id')})"

    print(body)


@app.command()
def get(id: int):
    """指定IDのスニペット本文を出力(使用回数カウントアップ)"""
    logger.debug(f"id: {id}")
    with get_db() as db:
        row = find_row(db, id)
        if row is None:
            raise typer.Exit(code=1)

        db[C.TABLE].update(row["id"], {"rate": (row.get("rate") or 0) + 1})
        body = body_remove_input_place(row)

    print(body)


@app.command()
def edit(id: int):
    """TUIエディタで編集"""
    from snip.editor import SnippetApp
    logger.debug(f"Calling edit function: id={id}")

    with get_db() as db:
        if find_row(db, id) is None:
            typer.echo(f"[ERROR] id={id} は存在しません", err=True)
            raise typer.Exit(code=1)

    try:
        SnippetApp(id).run()
    except Exception as e:
        logger.error(f"Error in edit command: {e}")
        raise typer.Exit(code=1) from e
