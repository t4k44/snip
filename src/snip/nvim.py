import re
import snip.constants as C
from enum import IntFlag


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


def output(db):
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
