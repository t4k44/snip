from pathlib import Path

# TODO: 設定ファイルから読み込み
TABLE          = "snippets"
TAG_TABLE      = "tags"

FISH_ABBR_FILE = "abbr.fish"
SKK_ABBR_DICT  = "abbr.dict"

CLIP_COPY_CMD  = ["copyq", "copy"]
CLIP_PASTE_CMD = ["copyq", "paste"]
ROFI_LENGTH    = 40     # rofi body表示文字数

TARGET_FIELD = ["trigger", "body", "memo", "abbr", "tags", "mode", "fish_cur_mark"]

# Class : Path
CNF_PATH  = Path.home() / ".config"
DB_PATH   = Path.home() / ".config" / "snip"
DB_FILE   = DB_PATH / "snippets.db"
NVIM_SNIP = CNF_PATH / "nvim" / "luasnippets"
FISH_ABBR = CNF_PATH / "fish" / FISH_ABBR_FILE
SKK_ABBR  = CNF_PATH / "ibus-skk" / SKK_ABBR_DICT
