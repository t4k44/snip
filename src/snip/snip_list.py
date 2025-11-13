#!/usr/bin/env python3

import json
import subprocess
import logging
import snip.constants as C
from sqlite_utils import Database


def rofi_name(db: Database, args):
    copyq  = "/opt/copyq-sqlite/bin/copyq"
    length = 40
    tag    = args.tag
    query  = f"""
        SELECT id, trigger, replace(substr(body, 0, {length}), char(10), '⏎ ') AS body,
               tags, replace(substr(memo, 0, {length}), char(10), '⏎ ') AS memo
        FROM snippets
        WHERE EXISTS (SELECT 1 FROM json_each(snippets.tags) WHERE value = ?)
        """

    rows = db.query(query, [tag])
    rows = [f"{int(row['id']):3d} : {row['trigger']}\t{row['body']}\t{row['memo']}\t{row['tags']}" for row in rows]

    try:
        choice = subprocess.run(["rofi", "-dmenu", "-p", "'Snippets'"], input="\n".join(rows),
                                stdout=subprocess.PIPE, text=True)
        if choice.returncode != 0:
            return

        body = db[C.TABLE].get(choice.stdout.split()[0])["body"]
        subprocess.run([copyq, "copy", body])
        subprocess.run([copyq, "paste"])
    except subprocess.CalledProcessError as e:
        logging.error("stdout: %s", e.stdout)
        logging.error("stderr: %s", e.stderr)


def fzf_select(db: Database):
    lines = []
    for row in db[C.TABLE].rows_where(order_by="id DESC"):
        body = "⏎ ".join(row["body"].splitlines())
        tags = json.loads(row["tags"])
        lngm = (tags[0] if tags and tags[0] != "name" else "txt")
        lngm = "vim" if lngm == "nvim" else lngm
        lines.append(f'{row["id"]}\t{row["trigger"]}\t{body}\t[tags: {",".join(tags)}]\t{lngm}')

    fzf = subprocess.Popen(
        ["fzf", "--with-nth=2,3,4", "--delimiter=\t", "--no-unicode", "--preview",
            f"sqlite3 {str(C.DB_FILE)} \"SELECT body || char(10) || '--------' || char(10) || "
            f"memo || char(10) || '--------' || char(10) || id || ':' || "
            f"tags FROM {C.TABLE} WHERE id = {{1}}\" | "
                   f"batcat -pl {{5}} --color=always",
            "--preview-window=right,50%,wrap",
            "--bind", "enter:accept",
            "--bind", f"ctrl-e:execute(sqlite-utils rows {str(C.DB_FILE)} {C.TABLE} --where \"id={{1}}\" "
                   f"--nl --json-cols | jq . > /tmp/snp_edit.json && nvim /tmp/snp_edit.json && "
                   f"sqlite-utils upsert {str(C.DB_FILE)} snippets /tmp/snp_edit.json --pk id)",
            "--bind", f"ctrl-d:execute(sqlite-utils query {str(C.DB_FILE)} "
                   f"\"DELETE FROM {C.TABLE} WHERE id={{1}}\")"
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    stdin_data = "\n".join(lines)
    stdout, _ = fzf.communicate(stdin_data)
    if not stdout:
        return ""

    # fzf returns the chosen line; id is first column
    chosen = stdout.strip().split("\n")[-1]
    id_selected = chosen.split("\t", 1)[0]

    # fetch full body
    row = db[C.TABLE].get(id_selected)
    return row["body"] if row else ""
