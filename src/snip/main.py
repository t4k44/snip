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
import snip.constants as C
import sys
from . import __version__
from pathlib        import Path
from snip.snip_list import fzf_select, rofi_name
from sqlite_utils   import Database


def insert_snip(db: Database, args, body: str):
    trigger = args.trigger or (None if not body else body.splitlines()[0][:40])
    tags = [t for t in args.tags.split(",") if t]

    with db.conn:
        if args.id:
            db[C.TABLE].upsert({
                "id":      args.id,
                "trigger": trigger,
                "body":    body,
                "memo":    args.memo,
                "abbr":    args.abbr,
                "tags":    json.dumps(tags),
                "mode":    args.mode,
            }, pk="id")
        else:
            db[C.TABLE].insert({
                "trigger": trigger,
                "body":    body,
                "memo":    args.memo,
                "abbr":    args.abbr,
                "tags":    json.dumps(tags),
                "mode":    args.mode,
            }, pk="id", columns={"abbr": int})
        ret = db[C.TABLE].get(db.conn.execute("SELECT last_insert_rowid()").fetchone()[0])

    return ret


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--version", action="version",
                   version=f"%(prog)s {__version__}",
                   help="バージョン表示")

    sub    = p.add_subparsers(dest="cmd")
    a_list = sub.add_parser("list")
    a_list.add_argument("-f", "--fzf",  action="store_true", help="commandline fzf selector")
    a_list.add_argument("-N", "--name", action="store_true", help="rofi app and so name")
    a_list.add_argument("-s", "--fish", action="store_true", help="output fish abbr")
    a_list.add_argument("-n", "--nvim", action="store_true", help="output luasnippets list")
    a_list.add_argument("-r", "--rofi", action="store_true", help="rofi内部使用用")

    a_add  = sub.add_parser("add")
    a_add.add_argument("-i", "--id",      default=None,   help="update id")
    a_add.add_argument("-T", "--trigger", default="memo", help="snippet trigger string")
    a_add.add_argument("-t", "--tags",    default="fish", help="tags split ','")
    a_add.add_argument("-b", "--body",    default=None,   help="expand strings")
    a_add.add_argument("-m", "--memo",    default="",     help="description")
    a_add.add_argument("-a", "--abbr",    default=0,      help="fish abbr  1:ON / 2:Position / 4:SetCursor")
    a_add.add_argument("-M", "--mode",    default=None,   help="nvim mode  t:ON / fmta:TabStop / raw:raw")

    args = p.parse_args()

    db_path = Path.home() / ".config" / "mine"
    db_path.mkdir(parents=True, exist_ok=True)
    db_file = db_path / C.DBNAME
    db = Database(str(db_file))

    match args.cmd:
        case "add":
            body = sys.stdin.read() if not sys.stdin.isatty() else (args.body or "")
            ret  = insert_snip(db, args, body)
            print(f"DONE {ret['id']} : {ret['trigger']}")
        case "list":
            if args.fzf:
                # `commandline -i (snip list -f)` で呼び出し
                print(fzf_select(db))
            elif args.name:
                rofi_name(db)
            elif args.fish:
                pass
            elif args.nvim:
                pass
            elif args.rofi:
                pass
            else:
                pass
        case _:
            pass


if __name__ == "__main__":
    main()
