from pathlib import Path

DBNAME    = "snippets.db"
TABLE     = "snippets"
TAG_TABLE = "tags"

CNF_PATH  = Path.home() / ".config"
DB_PATH   = CNF_PATH / "mine"
DB_FILE   = DB_PATH / DBNAME
NVIM_SNIP = CNF_PATH / "nvim" / "luasnippets"
FISH_ABBR = CNF_PATH / "fish" / "abbr.fish"
