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
import snip.constants as C
import sys
from . import __version__
from pathlib        import Path
from snip.snip_list import fzf_select
from sqlite_utils   import Database


def insert_snip(db: Database, args, body: str):
    trigger = args.trigger or (None if not body else body.splitlines()[0][:40])
    tags = [t for t in args.tags.split(",") if t]

    db[C.TABLE].insert({
        "trigger": trigger,
        "body":    body,
        "memo":    args.memo,
        "abbr":    args.abbr,
        "tags":    json.dumps(tags),
        "mode":    None,
    }, pk="id", columns={"abbr": int})


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--version", action="version",
                   version=f"%(prog)s {__version__}",
                   help="バージョン表示")

    sub    = p.add_subparsers(dest="cmd")
    a_list = sub.add_parser("list")
    a_add  = sub.add_parser("add")

    a_add.add_argument("-T", "--trigger", default=None)
    a_add.add_argument("-t", "--tags",    default="python")
    a_add.add_argument("-a", "--abbr",    default=0)
    a_add.add_argument("-m", "--memo",    default="")
    a_add.add_argument("-b", "--body",    default=None)
    args = p.parse_args()

    prj_path = Path.cwd()
    db = Database(str(prj_path / C.DBNAME))

    match args.cmd:
        case "add":
            body = sys.stdin.read() if not sys.stdin.isatty() else (args.body or "")
            insert_snip(db, args, body)
            print("ok")
        case "list":
            # `commandline -i (snip list)` で呼び出し
            print(fzf_select(db))
        case _:
            pass


if __name__ == "__main__":
    main()
