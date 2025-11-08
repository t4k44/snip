#!/usr/bin/env python3
"""
snip.py - simple snippet manager compatible with existing workflow.

Usage:
  snip.py list            # show snippets via fzf, prints selected body to stdout
  snip.py add [--trigger T] [--tags a,b] [--abbr N] [--memo M] [--body B]
  cat file | snip.py add  # read body from stdin
"""
import argparse
import json
import os
import shlex
import sqlite3
import subprocess
import sys
from typing import List

DB_PATH = os.path.expanduser("~/share/llogs.db")
TABLE = "snippets"

def ensure_table(conn: sqlite3.Connection):
    conn.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trigger TEXT,
        body TEXT,
        memo TEXT,
        abbr TEXT,
        tags TEXT,
        mime TEXT,
        source TEXT
    )""")
    conn.commit()

def insert_snip(conn: sqlite3.Connection, trigger: str, body: str, memo: str, abbr: str, tags: List[str]):
    tags_json = json.dumps(tags)
    conn.execute(f"INSERT INTO {TABLE} (trigger, body, memo, abbr, tags, mime, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 (trigger, body, memo, abbr, tags_json, "text/plain", "python"))
    conn.commit()

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
        body_one = r["body"].replace("\n", "
")  # keep visible but single-line
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

def main():
    p      = argparse.ArgumentParser()
    sub    = p.add_subparsers(dest="cmd")
    a_list = sub.add_parser("list")
    a_add  = sub.add_parser("add")

    a_add.add_argument("--trigger", "-T", default=None)
    a_add.add_argument("--tags",    "-t", default="python")
    a_add.add_argument("--abbr",    "-a", default="0")
    a_add.add_argument("--memo",    "-m", default="")
    a_add.add_argument("--body",    "-b", default=None)
    args = p.parse_args()

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    ensure_table(conn)

    if args.cmd == "add":
        if not sys.stdin.isatty() and args.body is None:
            body = sys.stdin.read()
        else:
            body = args.body or ""
        trigger = args.trigger or (None if not body else body.splitlines()[0][:40])
        tags = [t for t in args.tags.split(",") if t]
        insert_snip(conn, trigger or "", body, args.memo, args.abbr, tags)
        print("ok")
    else:
        body = fzf_select(DB_PATH)
        if body:
            # print body to stdout for shell-capture; caller can insert into commandline as needed
            sys.stdout.write(body)

if __name__ == "__main__":
    main()
