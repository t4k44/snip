#!/usr/bin/env python3
"""
usage: snip [-h] [--version] {list,add,edit} ...

snippet管理tool

options:
  -h, --help       show this help message and exit
  --version        バージョン表示

subcommands:
  主要コマンド

  {list,add,edit}
    list           snippet一覧表示 or 出力
    add            snippet追加
    edit           snippet編集


list mode arguments:
  fzf   : commandline fzf selector `commandline -i (snip list -f` で呼び出し
  rofi  : launch rofi and snip to clipboard
  fish  : output fish abbr
  nvim  : output luasnippets list
  skk   : output skk abbr

positional arguments:
  {fzf,rofi,fish,nvim,skk}

options:
  -h, --help            show this help message and exit
  -t TAG, --tag TAG     narrow down from tag


add mode arguments:
  trigger               snippet trigger string
  body                  expand strings

options:
  -h, --help            show this help message and exit
  -t TAGS, --tags TAGS  tags split ','
  -m MEMO, --memo MEMO  description
  -a {1,3,5,7}, --abbr {1,3,5,7}
                        fish abbr 1:ON / 2:Position / 4:SetCursor
  -M {t,fmta,raw}, --mode {t,fmta,raw}
                        nvim mode t:ON / fmta:TabStop / raw:raw

edit mode arguments:
  id                    update target id

options:
  -h, --help            show this help message and exit
  -t TAGS, --tags TAGS  tags split ','
  -m MEMO, --memo MEMO  description
  -a {1,3,5,7}, --abbr {1,3,5,7}
                        fish abbr 1:ON / 2:Position / 4:SetCursor
  -M {t,fmta,raw}, --mode {t,fmta,raw}
                        nvim mode t:ON / fmta:TabStop / raw:raw
  -T TRIGGER, --trigger TRIGGER
                        snippet trigger string
  -b BODY, --body BODY  expand strings
"""
import argparse
import textwrap
import snip.constants as C
import sys
from . import __version__
from snip.snip_list import fzf_select, rofi_name
import snip.snippets as SNIP
from snip import fish_abbr, nvim, skk
from sqlite_utils import Database


def args_parse():
    p = argparse.ArgumentParser(description='snippet管理tool')
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}",
                   help="バージョン表示")

    sub = p.add_subparsers(dest="cmd", required=True, description="主要コマンド")

    a_list = sub.add_parser("list", help="list mode arguments:",
        description=textwrap.dedent("""\
        list mode:
          fzf   : commandline fzf selector `commandline -i (snip list -f` で呼び出し
          rofi  : launch rofi and snip to clipboard
          fish  : output fish abbr
          nvim  : output luasnippets list
          skk   : output skk abbr
        """),
        formatter_class=argparse.RawTextHelpFormatter)
    a_list.add_argument("-t", "--tag", default="name", help="narrow down from tag")
    a_list.add_argument("mode", choices=["fzf", "rofi", "fish", "nvim", "skk"])

    # add, edit 共通引数
    a_parent = argparse.ArgumentParser(add_help=False)
    a_parent.add_argument("-t", "--tags",    default="fish", help="tags split ','")
    a_parent.add_argument("-m", "--memo",    default="",     help="description")
    a_parent.add_argument("-a", "--abbr",    default=0,      choices=[1,3,5,7],
                       help="fish abbr  1:ON / 2:Position / 4:SetCursor")
    a_parent.add_argument("-M", "--mode",    default=None,   choices=["t", "fmta", "raw"],
                       help="nvim mode  t:ON / fmta:TabStop / raw:raw")

    # add
    a_add = sub.add_parser("add", parents=[a_parent], help="add mode arguments:")
    a_add.add_argument("trigger", help="snippet trigger string")
    a_add.add_argument("body",    nargs='*', help="expand strings")

    # edit
    a_edt = sub.add_parser("edit", parents=[a_parent], help="edit mode arguments:")
    a_edt.add_argument("-T", "--trigger", default=None,      help="snippet trigger string")
    a_edt.add_argument("-b", "--body",    default=None,      help="expand strings")
    a_edt.add_argument("id", help="update target id")

    return p.parse_args()


def main():
    args = args_parse()

    C.DB_PATH.mkdir(parents=True, exist_ok=True)
    db = Database(str(C.DB_FILE))

    match args.cmd:
        case "add":
            args.body = sys.stdin.read() if not sys.stdin.isatty() else (" ".join(args.body) or "")
            ret  = SNIP.insert(db, args)
            print(f"DONE {ret['id']} : {ret['trigger']} / {ret['body']}")
        case "edit":
            ret  = SNIP.update(db, args)
            print(f"UPDATE {ret['id']} : {ret['trigger']} / {ret['body']}")
        case "list":
            match args.mode:
                case "fzf":
                    print(fzf_select(db))
                case "rofi":
                    rofi_name(db, args)
                case "fish":
                    fish_abbr.output(db)
                case "nvim":
                    nvim.output(db)
                case "skk":
                    skk.output(db)
                case _:
                    pass
        case _:
            pass


if __name__ == "__main__":
    main()
