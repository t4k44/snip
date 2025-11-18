#!/usr/bin/env python3
"""
snip.py - simple snippet manager compatible with existing workflow.

Usage:
  snip.py list            # show snippets via fzf, prints selected body to stdout
  snip.py add [--trigger T] [--tags a,b] [--abbr N] [--memo M] [--body B]
  cat file | snip.py add  # read body from stdin
"""
import argparse
import snip.constants as C
import sys
from . import __version__
from snip.snip_list import fzf_select, rofi_name
import snip.snippets as SNIP
from snip import fish_abbr, nvim, skk
from sqlite_utils import Database


def main():
    p = argparse.ArgumentParser(description='snippet管理tool')
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}",
                   help="バージョン表示")

    sub    = p.add_subparsers(dest="cmd")
    a_list = sub.add_parser("list")
    a_list.add_argument("-f", "--fzf",  action="store_true", help="""commandline fzf selector
        `commandline -i (snip list -f)` で呼び出し
    """)
    a_list.add_argument("-r", "--rofi", action="store_true", help="launch rofi and snip to clipboard")
    a_list.add_argument("-s", "--fish", action="store_true", help="output fish abbr")
    a_list.add_argument("-n", "--nvim", action="store_true", help="output luasnippets list")
    a_list.add_argument("-k", "--skk",  action="store_true", help="output skk abbr")
    a_list.add_argument("-t", "--tag",  default="name",      help="narrow down from tag")

    a_add = sub.add_parser("add")
    a_add.add_argument("-t", "--tags",    default="fish", help="tags split ','")
    a_add.add_argument("-m", "--memo",    default="",     help="description")
    a_add.add_argument("-a", "--abbr",    default=0,      help="fish abbr  1:ON / 2:Position / 4:SetCursor")
    a_add.add_argument("-M", "--mode",    default=None,   help="nvim mode  t:ON / fmta:TabStop / raw:raw")
    a_add.add_argument("trigger", nargs='?', help="snippet trigger string")
    a_add.add_argument("body",    nargs='*', help="expand strings")

    a_edt = sub.add_parser("edit")
    a_edt.add_argument("id", nargs='?',   help="update target id")
    a_edt.add_argument("-t", "--tags",    default="fish", help="tags split ','")
    a_edt.add_argument("-m", "--memo",    default="",     help="description")
    a_edt.add_argument("-a", "--abbr",    default=0,      help="fish abbr  1:ON / 2:Position / 4:SetCursor")
    a_edt.add_argument("-M", "--mode",    default=None,   help="nvim mode  t:ON / fmta:TabStop / raw:raw")
    a_edt.add_argument("-T", "--trigger", default=None,   help="snippet trigger string")
    a_edt.add_argument("-b", "--body",    default=None,   help="expand strings")

    args = p.parse_args()

    C.DB_PATH.mkdir(parents=True, exist_ok=True)
    db = Database(str(C.DB_FILE))

    match args.cmd:
        case "add":
            body = sys.stdin.read() if not sys.stdin.isatty() else (" ".join(args.body) or "")
            ret  = SNIP.insert(db, args, body)
            print(f"DONE {ret['id']} : {ret['trigger']} / {ret['body']}")
        case "edit":
            ret  = SNIP.update(db, args)
            print(f"UPDATE {ret['id']} : {ret['trigger']} / {ret['body']}")
        case "list":
            if args.fzf:
                # `commandline -i (snip list -f)` で呼び出し
                print(fzf_select(db))
            elif args.rofi:
                rofi_name(db, args)
            elif args.fish:
                fish_abbr.output(db)
            elif args.nvim:
                nvim.output(db)
            elif args.skk:
                skk.output(db)
            else:
                pass
        case _:
            pass


if __name__ == "__main__":
    main()
