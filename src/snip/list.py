import re
import shlex
import sys
from enum import IntFlag

import typer
from pyutils.logger import setup_logger
from rich.console import Console
from rich.table import Table
from sqlite_utils import Database

import snip.constants as C
from snip.snippets import AbbrFlag
from snip.utils import get_db

app = typer.Typer(help="(l) スニペットの一覧表示、各種アプリケーション用ファイル出力")
logging = setup_logger(__name__)


@app.command()
@app.command(name="cs", hidden=True)
def cheat_sheet(tag: str):
    """登録済みabbr表示"""
    with get_db() as db:
        table = Table(title=tag)
        table.add_column("abbr")
        table.add_column("cmd")
        table.add_column("memo")

        query = "EXISTS (SELECT 1 FROM json_each(snippets.tags) WHERE value = ?)"
        for row in db[C.TABLE].rows_where(query, [tag], order_by="trigger", select="trigger, body, memo"):
            table.add_row(row["trigger"], row["body"], row["memo"])

    Console().print(table)


@app.command()
def fish():
    """fish用abbr出力"""
    cmds = []
    with get_db() as db:
        for row in db["snippets"].rows_where("abbr & 1 = 1", select="trigger, body, abbr, fish_cur_mark"):
            flags = AbbrFlag(row["abbr"])
            if AbbrFlag.SIMPLE in flags:
                parts = ["abbr", "--add"]

                if AbbrFlag.POSITION_ANYWHERE in flags:
                    parts += ["--position", "anywhere"]

                if AbbrFlag.SET_CURSOR in flags:
                    if row["fish_cur_mark"]:
                        parts += [f"--set-cursor={row['fish_cur_mark']}"]
                    else:
                        parts += ["--set-cursor"]

                parts += ["--", row["trigger"], re.sub("<[0-9]>", "", row["body"])]
                cmds.append(" ".join(shlex.quote(p) for p in parts)) # 各引数をシェル安全にクォートして連結

        if not cmds:
            print("登録対象なし")
            return 0

        fish_cmd = "\n".join(cmds)
        try:
            file = open(C.FISH_ABBR, "w", encoding="UTF-8")
            file.writelines(fish_cmd)
            file.close()
        except Exception as e:
            print(f"[ERROR] 一括登録失敗: {e}", file=sys.stderr)
            return 1

    return 0


@app.command()
def skk(db):
    """SKKの辞書形式でスニペットを自動生成"""
    abbr = []
    with get_db() as db:
        rows = db[C.TABLE].rows_where(
            "EXISTS (SELECT 1 FROM json_each(snippets.tags) WHERE value = ?)", ['skk'])
        for row in rows:
            body  = row["body"].replace("%", "")
            abbr.append(f"{row['trigger']} /{body}/\n")

    file = open(C.SKK_ABBR, "w", encoding="UTF-8")
    file.write(";; okuri-ari entries.\n")
    file.write(";; okuri-nasi entries.\n")
    file.writelines(abbr)
    file.close()


def init_nvim_tag(db):
    tags = [
        {"name":"all"},{"name":"gitcommit"},{"name":"python"},
        {"name":"sh"},{"name":"sql"},{"name":"text"}
    ]
    db[C.TAG_TABLE].insert_all(tags, pk="id", columns={"abbr": int})


@app.command()
def nvim():
    """NeovimのLuaSnip形式でスニペットを自動生成"""
    with get_db() as db:
        for t in db[C.TAG_TABLE].rows:
            tag = t["name"]
            rows = db[C.TABLE].rows_where(
                "EXISTS (SELECT 1 FROM json_each(snippets.tags) WHERE value = ?)"
                "AND mode IS NOT NULL", [tag])

            snip = []
            for row in rows:
                match row["mode"]:
                    case "fmta":
                        body  = row["body"].replace("%", "")
                        maxn  = [int(m) for m in re.findall(r"<(\d+)>", body)]
                        nodes = ", ".join([f"i({n})" for n in maxn])
                        snip.append(f"  s(\"{row['trigger']}\", fmta([[{body}]], {{ {nodes} }})),\n")
                    case "raw":
                        snip.append(f"  s(\"{row['trigger']}\", {{{row['body']}}}),\n")
                    case "t":
                        body = row['body'].replace("\"", "\\\"").replace("\n", "\",\"")
                        snip.append(f"  s(\"{row['trigger']}\", t(\"{body}\")),\n")

            file_name = C.NVIM_SNIP / f"{tag}.lua"
            file = open(file_name, "w", encoding="UTF-8")
            file.write("local fmta = require(\"luasnip.extras.fmt\").fmta\n")
            file.write("return {\n")
            file.writelines(snip)
            file.write("}")
            file.close()
