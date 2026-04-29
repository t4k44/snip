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

# logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format='%(levelname)s: %(message)s')


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


def rofi_name(db: Database, args):
    tag    = args.tag or "name"
    query  = f"""
        SELECT id, trigger, replace(substr(body, 0, {C.ROFI_STRLEN}), char(10), '⏎ ') AS body,
               tags, replace(substr(memo, 0, {C.ROFI_STRLEN}), char(10), '⏎ ') AS memo
        FROM snippets
        WHERE EXISTS (SELECT 1 FROM json_each(snippets.tags) WHERE value = ?)
        ORDER BY rate DESC, id DESC
        """

    rows = db.query(query, [tag])
    rows = [f"{row['trigger']}\t / \t{row['body']}"
            f"\t{row['memo']}\t{row['tags']}\t{int(row['id']):04d}" for row in rows]

    try:
        choice = subprocess.run(C.ROFI, input="\n".join(rows),
                                stdout=subprocess.PIPE, text=True)
        if choice.returncode != 0:
            return

        target = db[C.TABLE].get(choice.stdout.split()[-1])

        db[C.TABLE].update(target["id"], {"rate": target["rate"] + 1})
        logging.info(target["body"])
        body = __body_clean_ip(target)
        logging.info(body)
        subprocess.run(C.CLIP_COPY_CMD + [body], check=True)
        time.sleep(0.1)
        subprocess.run(C.CLIP_PASTE_CMD, check=True)
        logging.info("done")

    except subprocess.CalledProcessError as e:
        logging.error("stdout: %s", e.stdout)
        logging.error("stderr: %s", e.stderr)


def fzf_select(db: Database, args: Namespace):
    lines = []

    query = f"EXISTS (SELECT 1 FROM json_each(snippets.tags) WHERE value = '{args.tag}')" if args.tag else None
    for row in db[C.TABLE].rows_where(query, order_by="rate DESC, id DESC"):
        body = __body_clean_ip(row)
        body = "⏎ ".join(body.splitlines())
        tags = json.loads(row["tags"])
        lngm = (tags[0] if tags and tags[0] != "name" else "txt")
        lngm = "vim" if lngm == "nvim" else lngm
        lines.append(f'{row["id"]}\t{row["trigger"]}\t{body}\t[tags: {",".join(tags)}]\t{lngm}')

    fzf = subprocess.Popen(
        ["fzf", "--with-nth=2,3,4", "--delimiter=\t", "--no-unicode", "--preview",
            f"sqlite3 {str(C.DB_FILE)} \"SELECT body || char(10) || '--------' || char(10) || "
            f"memo || char(10) || '--------' || char(10) || id || ':' || "
            f"tags FROM {C.TABLE} WHERE id = {{1}}\" | "
                   f"batcat -pl {{5}} --color=always",
            "--preview-window=right,50%,wrap",
            "--bind", "enter:accept",
            "--bind", f"ctrl-e:execute(sqlite-utils rows {str(C.DB_FILE)} {C.TABLE} --where \"id={{1}}\" "
                   f"--nl --json-cols | jq . > /tmp/snp_edit.json && nvim /tmp/snp_edit.json && "
                   f"sqlite-utils upsert {str(C.DB_FILE)} snippets /tmp/snp_edit.json --pk id)",
            "--bind", f"ctrl-d:execute(sqlite-utils query {str(C.DB_FILE)} "
                   f"\"DELETE FROM {C.TABLE} WHERE id={{1}}\")"
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    stdin_data = "\n".join(lines)
    stdout, _ = fzf.communicate(stdin_data)
    if not stdout:
        return ""

    # fzf returns the chosen line; id is first column
    chosen = stdout.strip().split("\n")[-1]
    id_selected = chosen.split("\t", 1)[0]

    # fetch full body
    row  = db[C.TABLE].get(id_selected)
    body = ""
    if row:
        db[C.TABLE].update(row["id"], {"rate": row["rate"] + 1})
        body = __body_clean_ip(row)

    return body


def cheat_sheet(db: Database, args: Namespace):
    if not args.tag:
        return

    table = Table(title=args.tag)
    # table.add_column("", justify="right", no_wrap=True)
    table.add_column("abbr")
    table.add_column("cmd")
    table.add_column("memo")

    query = "EXISTS (SELECT 1 FROM json_each(snippets.tags) WHERE value = ?)"
    for row in db[C.TABLE].rows_where(query, [args.tag], order_by="trigger",
                                      select="id, trigger, body, tags, memo"):
        tags = json.loads(row["tags"])
        table.add_row(row["trigger"], row["body"], row["memo"])

    Console().print(table)
