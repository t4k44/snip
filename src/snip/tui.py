import json

import typer
from pyutils.logger import setup_logger

import snip.constants as C
from snip.utils import body_remove_input_place, get_db

app = typer.Typer(help="tui parts")
logger = setup_logger(__name__)

@app.command()
def list(tag: str = typer.Argument("fish")):
    """fzfに渡すためのタブ区切り一覧を出力"""
    lines = []
    query = f"EXISTS (SELECT 1 FROM json_each(snippets.tags) WHERE value = '{tag}')"

    with get_db() as db:
        logger.debug(f"query: {query}")
        for row in db[C.TABLE].rows_where(query, order_by="rate DESC, id DESC"):
            body = body_remove_input_place(row)
            body = "⏎ ".join(body.splitlines())
            tags = json.loads(row["tags"])
            lngm = (tags[0] if tags and tags[0] != "name" else "txt")
            lngm = "vim" if lngm == "nvim" else lngm

            lines.append(f'{row["id"]}\t{row["trigger"]}\t{body}\t[tags: {",".join(tags)}]\t{lngm}')

    print("\n".join(lines))


@app.command()
def preview(id: int):
    """指定IDのスニペットのプレビューを表示"""
    logger.debug(f"id: {id}")
    with get_db() as db:
        row  = db[C.TABLE].get(id)
        if not row: return ""

        body  = body_remove_input_place(row)
        body += "\n---\n"
        body += row.get("memo", "")
        body += "\n---\n"
        body += f"{row.get("tags", "")} (id: {row.get("id")})"

    print(body)


@app.command()
def get(id: int):
    logger.debug(f"id: {id}")
    with get_db() as db:
        row  = db[C.TABLE].get(id)
        body = ""
        if row:
            db[C.TABLE].update(row["id"], {"rate": row["rate"] + 1})
            body = body_remove_input_place(row)

    print(body)


# TODO: snip edit <id>
# 編集 指定 ID を一時ファイルで開いて更新
@app.command()
def edit(id: int):
    pass
