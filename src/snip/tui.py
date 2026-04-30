import json
import logging
import re
import subprocess
import time
from argparse import Namespace

from rich.console import Console
from rich.table import Table
from sqlite_utils import Database

import snip.constants as C
from snip.fish_abbr import AbbrFlag


def __body_clean_ip(row):
    """
    bodyのカーソル位置指定用記号を除去する
    """
    # logging.debug("__body_clean_ip: 開始 (target['id']: %s)", row.get("id"))
    body = row["body"]
    if row.get("mode"):
        body = re.sub("<[0-9]>", "", body)

    if row.get("abbr") and AbbrFlag.SET_CURSOR in AbbrFlag(row["abbr"]):
        mark = row["fish_cur_mark"] or "%"
        body = body.replace(mark, "")

    return body


# サブコマンド 役割 出力イメージ
# snip list raw     fzf に渡す一覧 ID\tTrigger\tMemo\tTags...
# snip preview <id> プレビュー画面用 Body + --- + Memo (色付き)
# snip get     <id> 確定後の取得 Body のみ出力（ついでに rate を加算）
# snip edit    <id> 編集 指定 ID を一時ファイルで開いて更新
# snip delete  <id> 削除 指定 ID を物理削除
def raw(db: Database, args: Namespace):
    lines = []
    query = f"EXISTS (SELECT 1 FROM json_each(snippets.tags) WHERE value = '{args.tag}')" if args.tag else None

    for row in db[C.TABLE].rows_where(query, order_by="rate DESC, id DESC"):
        body = __body_clean_ip(row)
        body = "⏎ ".join(body.splitlines())
        tags = json.loads(row["tags"])
        lngm = (tags[0] if tags and tags[0] != "name" else "txt")
        lngm = "vim" if lngm == "nvim" else lngm
        lines.append(f'{row["id"]}\t{row["trigger"]}\t{body}\t[tags: {",".join(tags)}]\t{lngm}')

    return "\n".join(lines)

def preview(db: Database, args: Namespace):
    row  = db[C.TABLE].get(args.id)
    if not row: return ""

    body  = __body_clean_ip(row)
    body += "\n---\n"
    body += row.get("memo", "")

    return body

def get(db: Database, args: Namespace):
    row  = db[C.TABLE].get(args.id)
    body = ""
    if row:
        db[C.TABLE].update(row["id"], {"rate": row["rate"] + 1})
        body = __body_clean_ip(row)

    return body
