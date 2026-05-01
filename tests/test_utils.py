import pytest
from snip.utils import body_remove_input_place, AbbrFlag

def test_body_remove_input_place_no_modification():
    row = {"body": "hello world", "abbr": 0}
    assert body_remove_input_place(row) == "hello world"

def test_body_remove_input_place_mode_fmta():
    row = {"body": "hello <1> <2>", "abbr": 0, "mode": "fmta"}
    assert body_remove_input_place(row) == "hello  "

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

def test_body_remove_input_place_both():
    row = {
        "body": "echo <1> %",
        "abbr": AbbrFlag.SET_CURSOR.value,
        "mode": "fmta",
        "fish_cur_mark": "%"
    }
    assert body_remove_input_place(row) == "echo  "
