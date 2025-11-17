import re
import snip.constants as C
from enum import IntFlag
from sqlite_utils import Database


class AbbrFlag(IntFlag):
    SIMPLE            = 1
    POSITION_ANYWHERE = 2
    SET_CURSOR        = 4


def init(db):
    tags = [
        {"name":"all"},{"name":"gitcommit"},{"name":"python"},
        {"name":"sh"},{"name":"sql"},{"name":"text"}
    ]
    db[C.TAG_TABLE].insert_all(tags, pk="id", columns={"abbr": int})


def rows_from_tag(db: Database, tag: str):
    rows = db[C.TABLE].rows_where(
        "EXISTS (SELECT 1 FROM json_each(snippets.tags) WHERE value = ?)", [tag])

    return rows


def output(db):
    abbr = []
    for row in rows_from_tag(db, 'skk'):
        body  = row["body"].replace("%", "")
        abbr.append(f"{row['trigger']} /{body}/\n")

    file = open(C.SKK_ABBR, "w", encoding="UTF-8")
    file.write(";; okuri-ari entries.\n")
    file.write(";; okuri-nasi entries.\n")
    file.writelines(abbr)
    file.close()
