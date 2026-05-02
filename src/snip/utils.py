import re
from contextlib import contextmanager
from enum import IntFlag

from pyutils.db import get_db as get_raw_db

import snip.constants as C


@contextmanager
def get_db():
    """DB_PATHを固定してsqlite_utilsの接続を取得するラップ関数"""
    with get_raw_db(C.DB_FILE) as db:
        yield db


def body_remove_input_place(row):
    """
    bodyのカーソル位置指定用記号を除去する
    """
    body = row["body"]
    if row.get("mode"):
        body = re.sub("<[0-9]>", "", body)

    if row.get("abbr") and AbbrFlag.SET_CURSOR in AbbrFlag(row["abbr"]):
        mark = row["fish_cur_mark"] or "%"
        body = body.replace(mark, "")

    return body
