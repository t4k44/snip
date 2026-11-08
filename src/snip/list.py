import re
import shlex

import typer
from pyutils.logger import setup_logger
from rich.console import Console
from rich.markup import escape
from rich.table import Table

import snip.constants as C
from snip.models import PLACEHOLDER_RE, AbbrFlag
from snip.utils import get_db

app = typer.Typer(help="(l) スニペットの一覧表示、各種アプリケーション用ファイル出力")
logger = setup_logger(__name__)


@app.command()
@app.command(name="cs", hidden=True)
def cheat_sheet(tag: str):
    """登録済みabbr表示"""
    with get_db() as db:
        table = Table(title=escape(tag))
        table.add_column("abbr")
        table.add_column("cmd")
        table.add_column("memo")

        for row in db[C.TABLE].rows_where(C.TAG_FILTER, [tag], order_by="trigger", select="trigger, body, memo"):
            table.add_row(escape(row["trigger"] or ""), escape(row["body"] or ""), escape(row["memo"] or ""))

    Console().print(table)


@app.command()
def fish():
    """fish用abbr出力"""
    cmds = []
    with get_db() as db:
        for row in db[C.TABLE].rows_where("abbr & 1 = 1", select="trigger, body, abbr, fish_cur_mark"):
            flags = AbbrFlag(row["abbr"])
            parts = ["abbr", "--add"]

            if AbbrFlag.POSITION_ANYWHERE in flags:
                parts += ["--position", "anywhere"]

            if AbbrFlag.SET_CURSOR in flags:
                if row["fish_cur_mark"]:
                    parts += [f"--set-cursor={row['fish_cur_mark']}"]
                else:
                    parts += ["--set-cursor"]

            parts += ["--", row["trigger"], PLACEHOLDER_RE.sub("", row["body"] or "")]
            cmds.append(" ".join(shlex.quote(p) for p in parts))  # 各引数をシェル安全にクォートして連結

    if not cmds:
        print("登録対象なし")
        return

    try:
        C.FISH_ABBR.parent.mkdir(parents=True, exist_ok=True)
        C.FISH_ABBR.write_text("\n".join(cmds) + "\n", encoding="UTF-8")
    except OSError as e:
        typer.echo(f"[ERROR] 一括登録失敗: {e}", err=True)
        raise typer.Exit(code=1) from e


@app.command()
def skk():
    """SKKの辞書形式でスニペットを自動生成"""
    abbr = []
    with get_db() as db:
        for row in db[C.TABLE].rows_where(C.TAG_FILTER, ["skk"]):
            body = (row["body"] or "").replace("%", "")
            abbr.append(f"{row['trigger']} /{body}/\n")

    C.SKK_ABBR.parent.mkdir(parents=True, exist_ok=True)
    with open(C.SKK_ABBR, "w", encoding="UTF-8") as f:
        f.write(";; okuri-ari entries.\n")
        f.write(";; okuri-nasi entries.\n")
        f.writelines(abbr)


def _lua_str(s: str) -> str:
    """Luaの文字列リテラルに変換"""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


@app.command()
def nvim():
    """NeovimのLuaSnip形式でスニペットを自動生成"""
    C.NVIM_SNIP.mkdir(parents=True, exist_ok=True)
    with get_db() as db:
        for tag in (t["name"] for t in db[C.TAG_TABLE].rows):
            rows = db[C.TABLE].rows_where(f"{C.TAG_FILTER} AND mode IS NOT NULL", [tag])

            snip = []
            for row in rows:
                trig = _lua_str(row["trigger"] or "")
                body = row["body"] or ""
                match row["mode"]:
                    case "fmta":
                        body  = body.replace("%", "")
                        maxn  = max((int(m) for m in re.findall(r"<(\d+)>", body)), default=0)
                        nodes = ", ".join(f"i({n})" for n in range(1, maxn + 1))
                        snip.append(f"  s({trig}, fmta([==[{body}]==], {{ {nodes} }})),\n")
                    case "raw":
                        snip.append(f"  s({trig}, {{{body}}}),\n")
                    case "t":
                        lines = ", ".join(_lua_str(line) for line in body.split("\n"))
                        snip.append(f"  s({trig}, t({{{lines}}})),\n")

            with open(C.NVIM_SNIP / f"{tag}.lua", "w", encoding="UTF-8") as f:
                f.write("local fmta = require(\"luasnip.extras.fmt\").fmta\n")
                f.write("return {\n")
                f.writelines(snip)
                f.write("}")
