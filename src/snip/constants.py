from pathlib import Path

DBNAME = "snippets.db"
TABLE  = "snippets"
DB_PATH = Path.home() / ".config" / "mine"
DB_FILE = DB_PATH / DBNAME
