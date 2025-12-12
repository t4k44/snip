import snip.constants as C
from enum import IntFlag
import re
import shlex
import sys

class AbbrFlag(IntFlag):
    SIMPLE            = 1
    POSITION_ANYWHERE = 2
    SET_CURSOR        = 4


def output(db):
    cmds = []
    for row in db["snippets"].rows_where("abbr & 1 = 1", select="trigger, body, abbr, fish_cur_mark"):
        flags = AbbrFlag(row["abbr"])
        if AbbrFlag.SIMPLE in flags:
            parts = ["abbr", "--add"]

            if AbbrFlag.POSITION_ANYWHERE in flags:
                parts += ["--position", "anywhere"]

            if AbbrFlag.SET_CURSOR in flags:
                if row["fish_cur_mark"]:
                    parts += [f"--set-cursor={row['fish_cur_mark']}"]
                else:
                    parts += ["--set-cursor"]

            parts += ["--", row["trigger"], re.sub("<[0-9]>", "", row["body"])]
            # 各引数をシェル安全にクォートして連結
            cmds.append(" ".join(shlex.quote(p) for p in parts))

    if not cmds:
        print("登録対象なし")
        return 0

    fish_cmd = "\n".join(cmds)
    try:
        file = open(C.FISH_ABBR, "w", encoding="UTF-8")
        file.writelines(fish_cmd)
        file.close()
    except Exception as e:
        print(f"[ERROR] 一括登録失敗: {e}", file=sys.stderr)
        return 1

    return 0
