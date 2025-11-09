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
import sqlite3
import sys
from typing import List
from . import __version__
from .snip_list import fzf_select
import snip.constants as C

def ensure_table(conn: sqlite3.Connection):
    conn.execute(f"""CREATE TABLE IF NOT EXISTS {C.TABLE} (
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
    conn.execute(f"INSERT INTO {C.TABLE} (trigger, body, memo, abbr, tags, mime, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 (trigger, body, memo, abbr, tags_json, "text/plain", "python"))
    conn.commit()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}",
                        help="バージョン表示")

    sub    = p.add_subparsers(dest="cmd")
    a_list = sub.add_parser("list")
    a_add  = sub.add_parser("add")

    a_add.add_argument("-T", "--trigger", default=None)
    a_add.add_argument("-t", "--tags",    default="python")
    a_add.add_argument("-a", "--abbr",    default="0")
    a_add.add_argument("-m", "--memo",    default="")
    a_add.add_argument("-b", "--body",    default=None)
    args = p.parse_args()

    os.makedirs(os.path.dirname(os.path.expanduser(C.DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(os.path.expanduser(C.DB_PATH))
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
