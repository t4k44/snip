import re
from enum import IntFlag

# nvim(LuaSnip fmta) 用のタブストップ記号 <1>, <10> ...
PLACEHOLDER_RE = re.compile(r"<\d+>")

# fish abbr のカーソル位置マーク(既定)
DEFAULT_CURSOR_MARK = "%"


class AbbrFlag(IntFlag):
    SIMPLE            = 1
    POSITION_ANYWHERE = 2
    SET_CURSOR        = 4
