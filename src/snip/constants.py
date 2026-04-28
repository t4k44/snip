import os
from pathlib import Path

from pyutils.config import load_config

APP_NAME = "snip"

DEFAULTS = {
    # paths
    "db_file": "snippets.db",

    "nvim_snip_dir":  "nvim/luasnippets",
    "fish_abbr_file": "fish/abbr.fish",
    "skk_abbr_file":  "ibus-skk/abbr.dict",

    # db
    "table": "snippets",
    "tag_table": "tags",
    "target_field": [
        "trigger",
        "body",
        "memo",
        "abbr",
        "tags",
        "mode",
        "fish_cur_mark",
    ],

    # apps
    "rofi":        ["rofi", "-dmenu",   "-p", "Snippets"],
    "rofi_strlen": 40,
    "fzf":         ["fzf",  "--header", "Snippets"],

    "copy_cmd":  ["copyq", "copy"],
    "paste_cmd": ["copyq", "paste"],
}


CONFIG = load_config(APP_NAME, DEFAULTS, section_names=["paths", "db", "apps"])

CONFIG_DIR     = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
TABLE          = CONFIG["TABLE"]
TAG_TABLE      = CONFIG["TAG_TABLE"]

CLIP_COPY_CMD  = CONFIG["COPY_CMD"]
CLIP_PASTE_CMD = CONFIG["PASTE_CMD"]
ROFI           = CONFIG["ROFI"]
ROFI_STRLEN    = CONFIG["ROFI_STRLEN"]

DB_PATH        = CONFIG_DIR / APP_NAME
DB_FILE        = DB_PATH    / CONFIG["DB_FILE"]
NVIM_SNIP      = CONFIG_DIR / CONFIG["NVIM_SNIP_DIR"]
FISH_ABBR      = CONFIG_DIR / CONFIG["FISH_ABBR_FILE"]
SKK_ABBR       = CONFIG_DIR / CONFIG["SKK_ABBR_FILE"]
TARGET_FIELD   = CONFIG["TARGET_FIELD"]
