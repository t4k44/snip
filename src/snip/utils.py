from contextlib import contextmanager

from pyutils.db import get_db as get_raw_db
from sqlite_utils.db import NotFoundError

import snip.constants as C
from snip.models import DEFAULT_CURSOR_MARK, PLACEHOLDER_RE, AbbrFlag


DEFAULT_NVIM_TAGS = ["all", "gitcommit", "python", "sh", "sql", "text"]


@contextmanager
def get_db():
    """DB_PATHを固定してsqlite_utilsの接続を取得するラップ関数"""
    with get_raw_db(C.DB_FILE) as db:
        ensure_schema(db)
        yield db


def ensure_schema(db):
    """テーブルが無ければ正規スキーマで作成する(既存DBには何もしない)"""
    if C.TABLE not in db.table_names():
        db[C.TABLE].create(
            {
                "id": int, "trigger": str, "body": str, "memo": str, "abbr": int,
                "tags": str, "mode": str, "rate": int, "fish_cur_mark": str,
            },
            pk="id",
            not_null={"rate"},
            defaults={"trigger": "", "body": "", "memo": "", "abbr": 0, "tags": "[]", "rate": 0},
        )

    if C.TAG_TABLE not in db.table_names():
        db[C.TAG_TABLE].create({"name": str}, pk="name")
        db[C.TAG_TABLE].insert_all({"name": n} for n in DEFAULT_NVIM_TAGS)


def find_row(db, row_id):
    """IDで1行取得。存在しなければ None"""
    try:
        return db[C.TABLE].get(row_id)
    except NotFoundError:
        return None


def body_remove_input_place(row):
    """
    bodyのカーソル位置指定用記号を除去する
    """
    body = row.get("body") or ""
    if row.get("mode"):
        body = PLACEHOLDER_RE.sub("", body)

    if row.get("abbr") and AbbrFlag.SET_CURSOR in AbbrFlag(row["abbr"]):
        mark = row.get("fish_cur_mark") or DEFAULT_CURSOR_MARK
        body = body.replace(mark, "")

    return body
