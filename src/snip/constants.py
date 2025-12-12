from pathlib import Path

DBNAME         = "snippets.db"
TABLE          = "snippets"
TAG_TABLE      = "tags"

FISH_ABBR_FILE = "abbr.fish"
SKK_ABBR_DICT  = "abbr.dict"

COPYQ          = "/opt/copyq-sqlite/bin/copyq"
ROFI_LENGTH    = 40     # rofi body表示文字数

TARGET_FIELD = ["trigger", "body", "memo", "abbr", "tags", "mode", "fish_cur_mark"]

# Class : Path
CNF_PATH  = Path.home() / ".config"
DB_PATH   = CNF_PATH / "mine"
DB_FILE   = DB_PATH  / DBNAME
NVIM_SNIP = CNF_PATH / "nvim" / "luasnippets"
FISH_ABBR = CNF_PATH / "fish" / FISH_ABBR_FILE
SKK_ABBR  = CNF_PATH / "ibus-skk" / SKK_ABBR_DICT
