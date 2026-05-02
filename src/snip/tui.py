import json

import typer
from pyutils.logger import setup_logger

import snip.constants as C
from snip.utils import body_remove_input_place, get_db

app = typer.Typer(help="tui用低レベルコマンド")
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


@app.command()
def edit(id: int):
    from snip.editor import SnippetApp
    logger.debug(f"Calling edit function: id={id}")

    try:
        logger.debug(f"Initializing SnippetApp with id: {id}")
        app = SnippetApp(id)
        app.run()

    except Exception as e:
        logger.error(f"Error in edit command: {e}")


#@app.command()
#def edit(id: int):
#    """編集 指定IDを一時ファイルで開いて更新"""
#    import os
#    import subprocess
#    import tempfile
#
#    logger.debug(f"id: {id}")
#    with get_db() as db:
#        row  = db[C.TABLE].get(id)
#
#        if isinstance(row.get("tags"), str):
#            try:
#                row["tags"] = json.loads(row["tags"])
#            except json.JSONDecodeError:
#                pass # JSON形式でない場合はそのまま
#
#        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=True) as tf:
#            json.dump(row, tf, indent=4, ensure_ascii=False)
#            tf.flush()      # ディスクに書き込みを確定
#
#            # エディタ起動
#            # editor = os.environ.get('EDITOR', 'nvim')
#            subprocess.run([C.EDITOR, tf.name])
#
#            # 反映（エディタ終了後）
#            tf.seek(0)
#            updated_data = json.load(tf)
#
#            if updated_data != row:
#                if "tags" in updated_data and not isinstance(updated_data["tags"], str):
#                    updated_data["tags"] = json.dumps(updated_data["tags"], ensure_ascii=False)
#
#                db[C.TABLE].upsert(updated_data, pk="id")
#                print(f"Snippet {id} updated.")
#            else:
#                print("No changes detected.")
