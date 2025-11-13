import json
import snip.constants as C
from sqlite_utils   import Database

def insert_snip(db: Database, args, body: str):
    trigger = args.trigger or (None if not body else body.splitlines()[0][:40])
    tags = [t for t in args.tags.split(",") if t]

    with db.conn:
        if args.id:
            db[C.TABLE].upsert({
                "id":      args.id,
                "trigger": trigger,
                "body":    body,
                "memo":    args.memo,
                "abbr":    args.abbr,
                "tags":    json.dumps(tags),
                "mode":    args.mode,
            }, pk="id")
        else:
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


