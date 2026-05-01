import json

import typer
from pyutils.logger import setup_logger

import snip.constants as C
from snip.utils import body_remove_input_place, get_db

app = typer.Typer(help="tui parts")
logger = setup_logger(__name__)

# サブコマンド 役割 出力イメージ
# snip list raw     fzf に渡す一覧 ID\tTrigger\tMemo\tTags...
# snip preview <id> プレビュー画面用 Body + --- + Memo (色付き)
# snip get     <id> 確定後の取得 Body のみ出力（ついでに rate を加算）
# snip edit    <id> 編集 指定 ID を一時ファイルで開いて更新
# snip delete  <id> 削除 指定 ID を物理削除
@app.command()
def raw(tag: str = typer.Argument("fish")):
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
    logger.debug(f"id: {id}")
    with get_db() as db:
        row  = db[C.TABLE].get(id)
        if not row: return ""

        body  = body_remove_input_place(row)
        body += "\n---\n"
        body += row.get("memo", "")

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
