#!/usr/bin/env python3

import subprocess
import snip.constants as C
from sqlite_utils import Database
from pathlib import Path


def fzf_select(db: Database):
    lines = []
    for row in db[C.TABLE].rows:
        body_one = row["body"]
        tag0 = (row["tags"][0] if row["tags"] else "plain")
        lines.append(f'{row["id"]}\t{row["trigger"]}\t{body_one}\t[{",".join(row["tags"])}]\t{tag0}')

    prj_path = Path.cwd()
    fzf = subprocess.Popen(
        ["fzf", "--with-nth=2,3,4", "--delimiter=\t", "--no-unicode", "--preview",
         f"sqlite3 {str(prj_path / C.DBNAME)} \"SELECT body || char(10) || '--------' || char(10) || "
                f"memo || char(10) || '--------' || char(10) || tags FROM {C.TABLE} WHERE id = {{1}}\" | "
                f"batcat -pl {{5}} --color=always",
         "--preview-window=right,50%,wrap",
         "--bind", "enter:accept"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    stdin_data = "\n".join(lines)
    stdout, _ = fzf.communicate(stdin_data)
    if not stdout:
        return None

    # fzf returns the chosen line; id is first column
    chosen = stdout.strip().split("\n")[-1]
    id_selected = chosen.split("\t", 1)[0]

    # fetch full body
    row = db[C.TABLE].get(id_selected)["body"]
    return row["body"] if row else None
