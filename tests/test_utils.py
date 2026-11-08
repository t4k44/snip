import snip.constants as C
from snip.models import AbbrFlag
from snip.utils import body_remove_input_place, ensure_schema, find_row


def test_body_remove_input_place_no_modification():
    row = {"body": "hello world", "abbr": 0}
    assert body_remove_input_place(row) == "hello world"

def test_body_remove_input_place_mode_fmta():
    row = {"body": "hello <1> <2>", "abbr": 0, "mode": "fmta"}
    assert body_remove_input_place(row) == "hello  "

def test_body_remove_input_place_two_digit_placeholder():
    row = {"body": "a <10> b", "mode": "fmta"}
    assert body_remove_input_place(row) == "a  b"

def test_body_remove_input_place_abbr_cursor():
    row = {
        "body": "git commit -m '%'",
        "abbr": AbbrFlag.SET_CURSOR.value,
        "fish_cur_mark": "%"
    }
    assert body_remove_input_place(row) == "git commit -m ''"

def test_body_remove_input_place_abbr_cursor_default_mark():
    row = {
        "body": "hello % world",
        "abbr": AbbrFlag.SET_CURSOR.value,
        "fish_cur_mark": None
    }
    assert body_remove_input_place(row) == "hello  world"

def test_body_remove_input_place_missing_keys():
    row = {"body": "x %", "abbr": AbbrFlag.SET_CURSOR.value}  # fish_cur_mark キー無し
    assert body_remove_input_place(row) == "x "

def test_body_remove_input_place_both():
    row = {
        "body": "echo <1> %",
        "abbr": AbbrFlag.SET_CURSOR.value,
        "mode": "fmta",
        "fish_cur_mark": "%"
    }
    assert body_remove_input_place(row) == "echo  "

def test_ensure_schema_creates_table(db):
    ensure_schema(db)
    cols = {c.name: c for c in db[C.TABLE].columns}
    assert set(cols) == {"id", "trigger", "body", "memo", "abbr", "tags", "mode", "rate", "fish_cur_mark"}
    assert cols["rate"].notnull

    db[C.TABLE].insert({"trigger": "x"})
    row = db[C.TABLE].get(1)
    assert row["rate"] == 0
    assert row["abbr"] == 0
    assert row["tags"] == "[]"
    assert row["body"] == ""

def test_ensure_schema_keeps_existing_table(db):
    db[C.TABLE].insert({"only": 1})
    ensure_schema(db)
    assert [c.name for c in db[C.TABLE].columns] == ["only"]

def test_find_row(init_db):
    init_db[C.TABLE].insert({"trigger": "x"})
    assert find_row(init_db, 1)["trigger"] == "x"
    assert find_row(init_db, 999) is None

def test_ensure_schema_creates_tags_table(db):
    ensure_schema(db)
    assert [c.name for c in db[C.TAG_TABLE].columns] == ["name"]
    assert db[C.TAG_TABLE].pks == ["name"]
    assert {r["name"] for r in db[C.TAG_TABLE].rows} == {"all", "gitcommit", "python", "sh", "sql", "text"}

def test_ensure_schema_adds_tags_to_snippets_only_db(db):
    db[C.TABLE].insert({"trigger": "x"})
    ensure_schema(db)
    assert C.TAG_TABLE in db.table_names()
