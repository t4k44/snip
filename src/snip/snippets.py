import json
import snip.constants as C
from sqlite_utils import Database

def dict_pickup(target: dict, fields: list):
    """dict targetからfieldsを抽出。値がNoneの場合は除外"""
    ret_dict = {}
    for k in fields:
        val = target.get(k)
        if val is not None:
            ret_dict[k] = val
    return ret_dict


def insert(db: Database, args, body: str):
    trigger = args.trigger or (None if not body else body.splitlines()[0][:40])
    tags    = [t for t in args.tags.split(",") if t]

    with db.conn:
        db[C.TABLE].insert({
            "trigger": trigger,
            "body":    body,
            "memo":    args.memo,
            "abbr":    args.abbr,
            "tags":    json.dumps(tags),
            "mode":    args.mode,
        }, pk="id", columns={"abbr": int})
        ret = db[C.TABLE].get(db.conn.execute("SELECT last_insert_rowid()").fetchone()[0])

    return ret


def update(db: Database, args):
    target_field = ["trigger", "body", "memo", "abbr", "tags", "mode"]

    with db.conn:
        target = db[C.TABLE].get(args.id)
        target.update(dict_pickup(vars(args), target_field))
        target.update({"tags": [t for t in args.tags.split(",") if t]})

        db[C.TABLE].upsert(target, pk="id")
        ret = db[C.TABLE].get(args.id)

    return ret


