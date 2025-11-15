from pathlib import Path

DBNAME    = "snippets.db"
TABLE     = "snippets"
TAG_TABLE = "tags"
DB_PATH = Path.home() / ".config" / "mine"
DB_FILE = DB_PATH / DBNAME
