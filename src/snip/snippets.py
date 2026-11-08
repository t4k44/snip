import sys
from typing import Annotated

import typer
from pyutils.logger import setup_logger

import snip.constants as C
from snip.models import AbbrFlag
from snip.utils import find_row, get_db

logger = setup_logger(__name__)
app = typer.Typer()

# add/editで共通するオプションを定義
CommonTags = Annotated[str | None, typer.Option("--tags", "-t", help="tags split ','")]
CommonMemo = Annotated[str | None, typer.Option("--memo", "-m", help="description")]
CommonMode = Annotated[str | None, typer.Option("--mode", "-M",
                                                help="nvim mode  t:ON / fmta:TabStop / raw:raw")]
CommonMark = Annotated[str | None, typer.Option("--csr_mark", "-C",
                                                help="カーソル位置指定マーク設定")]

# フラグ類 (未指定=None, 明示的にOFFも可能)
Abbr = Annotated[bool | None, typer.Option("--abbr/--no-abbr",         "-a", help="fish abbrを有効")]
Pos  = Annotated[bool | None, typer.Option("--position/--no-position", "-p", help="fish abbr Anywhereを有効")]
Csr  = Annotated[bool | None, typer.Option("--cursor/--no-cursor",     "-c", help="fish abbr カーソル位置指定を有効")]


def _split_tags(tags: str | None) -> list[str] | None:
    if tags is None:
        return None
    return [t.strip() for t in tags.split(",") if t.strip()]


def _abbr_value(f_abbr: bool | None, f_position: bool | None, f_cursor: bool | None) -> int | None:
    """フラグ指定からabbr値を組み立てる。全て未指定なら None(=変更しない)"""
    if f_abbr is None and f_position is None and f_cursor is None:
        return None

    value = AbbrFlag(0)
    if f_position: value |= AbbrFlag.POSITION_ANYWHERE
    if f_cursor:   value |= AbbrFlag.SET_CURSOR
    if f_abbr or value: value |= AbbrFlag.SIMPLE   # Position/Cursor は abbr 有効が前提
    return int(value)


def _drop_none(params: dict) -> dict:
    return {k: v for k, v in params.items() if v is not None}


@app.command()
@app.command(name="a", hidden=True)
def add(
    trigger:       Annotated[str | None,       typer.Argument(help="abbr trigger")] = None,
    body:          Annotated[list[str] | None, typer.Argument(help="abbr body")] = None,
    tags:          CommonTags = "fish",
    memo:          CommonMemo = "",
    mode:          CommonMode = None,
    f_abbr:        Abbr       = None,
    f_position:    Pos        = None,
    f_cursor:      Csr        = None,
    fish_cur_mark: CommonMark = None,
):
    """(a) 新しいスニペットを追加"""
    logger.debug(f"trigger: {trigger}")

    body_text = " ".join(body) if body else None
    if body_text is None and not sys.stdin.isatty():
        logger.debug("reading body from stdin...")
        body_text = sys.stdin.read().strip()

    params = _drop_none({
        "trigger":       trigger,
        "body":          body_text,
        "tags":          _split_tags(tags),
        "memo":          memo,
        "mode":          mode,
        "abbr":          _abbr_value(f_abbr, f_position, f_cursor),
        "fish_cur_mark": fish_cur_mark,
    })
    logger.debug(f"calling SNIP.insert | params: {params}")

    with get_db() as db:
        table = db[C.TABLE]
        table.insert(params)
        ret = table.get(table.last_pk)
        typer.echo(f"DONE {ret['id']} : {ret['trigger']}")


@app.command()
@app.command(name="e", hidden=True)
def edit(
    id:            int,
    trigger:       Annotated[str | None, typer.Option("--trigger", "-T")] = None,
    body:          Annotated[str | None, typer.Option("--body",    "-b", help="'-' で標準入力から読む")] = None,
    tags:          CommonTags = None,
    memo:          CommonMemo = None,
    mode:          CommonMode = None,
    f_abbr:        Abbr       = None,
    f_position:    Pos        = None,
    f_cursor:      Csr        = None,
    fish_cur_mark: CommonMark = None,
):
    """(e) 既存のスニペットを編集"""
    logger.debug(f"trigger: {trigger}")

    if body == "-":
        body = sys.stdin.read().strip()

    params = _drop_none({
        "trigger":       trigger,
        "body":          body,
        "tags":          _split_tags(tags),
        "memo":          memo,
        "mode":          mode,
        "abbr":          _abbr_value(f_abbr, f_position, f_cursor),
        "fish_cur_mark": fish_cur_mark,
    })
    logger.debug(f"calling SNIP.edit | params: {params}")

    with get_db() as db:
        if find_row(db, id) is None:
            typer.echo(f"[ERROR] id={id} は存在しません", err=True)
            raise typer.Exit(code=1)

        if params:
            db[C.TABLE].update(id, params)
        ret = db[C.TABLE].get(id)
        logger.debug(f"calling SNIP.edit | record: {ret}")
        typer.echo(f"UPDATE {ret['id']} : {ret['trigger']}")


@app.command()
@app.command(name="d", hidden=True)
def delete(id: int):
    """(d) スニペットを削除します"""
    with get_db() as db:
        ret = find_row(db, id)
        if ret is None:
            typer.echo(f"[ERROR] id={id} は存在しません", err=True)
            raise typer.Exit(code=1)

        db[C.TABLE].delete(id)
        typer.echo("DELETED:")
        typer.echo(ret)
