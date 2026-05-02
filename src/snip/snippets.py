import sys
from typing import List, Optional

import typer
from pyutils.logger import setup_logger
from rich import print
from typing_extensions import Annotated

import snip.constants as C
from snip.utils import get_db

logger = setup_logger(__name__)
app = typer.Typer()

# add/editで共通するオプションを定義
CommonTags = Annotated[str, typer.Option("--tags", "-t", help="tags split ','")]
CommonMemo = Annotated[str, typer.Option("--memo", "-m", help="description")]
CommonMode = Annotated[Optional[str], typer.Option("--mode", "-M",
                                                   help="nvim mode  t:ON / fmta:TabStop / raw:raw")]
CommonMark = Annotated[Optional[str], typer.Option("--csr_mark", "-C",
                                                   help="カーソル位置指定マーク設定")]

# フラグ類
Abbr = Annotated[bool, typer.Option("--abbr",     "-a", help="fish abbrを有効")]
Pos  = Annotated[bool, typer.Option("--position", "-p", help="fish abbr Anywhereを有効")]
Csr  = Annotated[bool, typer.Option("--cursor",   "-c", help="fish abbr カーソル位置指定を有効")]


class AbbrFlag(IntFlag):
    SIMPLE            = 1
    POSITION_ANYWHERE = 2
    SET_CURSOR        = 4


@app.command()
@app.command(name="a", hidden=True)
def add(
    trigger: str,
    body: List[str],
    tags: CommonTags = "fish",
    memo: CommonMemo = "",
    mode: CommonMode = None,
    f_abbr:     Abbr = False,
    f_position: Pos  = False,
    f_cursor:   Csr  = False,
    fish_cur_mark: CommonMark = None,
):
    """(a) 新しいスニペットを追加"""
    logger.debug(f"trigger: {trigger}")

    with get_db() as db:
        params = __build_params(locals())
        logger.debug(f"calling SNIP.insert | params: {params}")

        db[C.TABLE].insert(params, pk="id", columns={"abbr": int})
        ret = db[C.TABLE].get(db.conn.execute("SELECT last_insert_rowid()").fetchone()[0])
        print(f"DONE {ret['id']} : {ret['trigger']}")


@app.command()
@app.command(name="e", hidden=True)
def edit(
    id: int,
    trigger: Annotated[Optional[str], typer.Option("--trigger", "-T")] = None,
    body: Annotated[Optional[str],    typer.Option("--body", "-b")] = None,
    tags: CommonTags = "fish",
    memo: CommonMemo = "",
    mode: CommonMode = None,
    f_abbr:     Abbr = False,
    f_position: Pos  = False,
    f_cursor:   Csr  = False,
    fish_cur_mark: CommonMark = None,
):
    """(e) 既存のスニペットを編集"""
    logger.debug(f"trigger: {trigger}")

    with get_db() as db:
        params = __build_params(locals())
        logger.debug(f"calling SNIP.insert | params: {params}")

        params["id"] = id
        db[C.TABLE].upsert(params, pk="id")
        ret = db[C.TABLE].get(id)
        print(f"UPDATE {ret['id']} : {ret['trigger']}")


@app.command()
@app.command(name="d", hidden=True)
def delete(id: int):
    """(d) スニペットを削除します"""
    with get_db() as db:
        ret = db[C.TABLE].get(id)
        db[C.TABLE].delete(id)

        print("DELETED:")
        print(ret)


def __build_params(local_vars: dict):
    """locals()からparams組み立て"""
    params = {
        k: local_vars[k]
        for k in C.TARGET_FIELD
        if k in local_vars and local_vars[k]    # 空文字、None除外
    }

    # bodyの処理
    if not sys.stdin.isatty():
        logger.debug("reading from stdin...")
        params["body"] = sys.stdin.read().strip()
    elif local_vars.get("body"):
        params["body"] = " ".join(local_vars.get("body", [])) or ""

    params["tags"] = [t for t in local_vars.get("tags").split(",") if t]

    flag = 0
    if local_vars.get("f_position"):          flag += 2
    if local_vars.get("f_cursor"):            flag += 4
    if local_vars.get("f_abbr") or flag != 0: flag += 1
    params["abbr"] = flag

    return params
