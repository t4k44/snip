#!/usr/bin/env python3

import sqlite3
import subprocess
import json
import shlex
from .constants import TABLE

def list_rows_json(conn: sqlite3.Connection):
    cur = conn.execute(f"SELECT id, trigger, body, memo, abbr, tags FROM {TABLE} ORDER BY id DESC")
    out = []
    for row in cur:
        id_, trigger, body, memo, abbr, tags = row
        try:
            tags_list = json.loads(tags) if tags else []
        except Exception:
            tags_list = [s for s in (tags or "").split(",") if s]
        out.append({
            "id": id_, "trigger": trigger, "body": body or "", "memo": memo or "", "abbr": abbr or "0", "tags": tags_list
        })
    return out


def fzf_select(db_path: str):
    # Build fzf input lines: id<TAB>trigger<TAB>body-as-single-line<TAB>tag0
    conn = sqlite3.connect(db_path)
    rows = list_rows_json(conn)
    conn.close()
    lines = []
    for r in rows:
#        body_one = r["body"].replace("\n", """
#""")  # keep visible but single-line
        body_one = r["body"]
        tag0 = (r["tags"][0] if r["tags"] else "plain")
        lines.append(f'{r["id"]}\t{r["trigger"]}\t{body_one}\t[{",".join(r["tags"])}]\t{tag0}')

    fzf = subprocess.Popen(
        ["fzf", "--with-nth=2,3,4", "--delimiter=\t", "--no-unicode",
         "--preview", f"sqlite3 {shlex.quote(db_path)} \"SELECT body || char(10) || '--------' || char(10) || memo || char(10) || '--------' || char(10) || tags FROM {TABLE} WHERE id = {{1}}\" | batcat -pl {{5}} --color=always",
         "--preview-window=right,50%,wrap",
         "--bind", "enter:accept"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    stdin_data = "\n".join(lines)
    stdout, _ = fzf.communicate(stdin_data)
    if not stdout:
        return None
    # fzf returns the chosen line; id is first column
    chosen = stdout.strip().split("\n")[-1]
    id_selected = chosen.split("\t", 1)[0]
    # fetch full body
    conn = sqlite3.connect(db_path)
    cur = conn.execute(f"SELECT body FROM {TABLE} WHERE id = ?", (id_selected,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


