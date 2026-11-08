import json

from pyutils.logger import setup_logger
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, Label, SelectionList, Static, TextArea

import snip.constants as C
from snip.models import AbbrFlag
from snip.utils import find_row, get_db

logger = setup_logger(__name__)


class SnippetEditor(Static):
    BINDINGS = [
        ("alt+t", "focus_trig"),
        ("alt+b", "focus_body"),
        ("alt+m", "focus_memo"),
        ("alt+g", "focus_tags"),
        ("alt+a", "focus_abbr"),
    ]

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data or {}
        logger.debug(f"SnippetEditor.__init__: initial_data={self.data}")

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("[u]T[/u]rigger:")
            yield Input(id="snippet-trigger", value=self.data.get("trigger") or "")

            yield Label("[u]B[/u]ody:")
            yield TextArea(id="snippet-body", text=self.data.get("body") or "")

            yield Label("[u]M[/u]emo:")
            yield TextArea(id="snippet-memo", text=self.data.get("memo") or "")

            raw_tags = self.data.get("tags")
            try:
                tags_list = json.loads(raw_tags) if raw_tags else []
                tags_str = ','.join(tags_list)
            except (json.JSONDecodeError, TypeError):
                tags_str = ""
            yield Label("Ta[u]g[/u]s:")
            yield Input(id="snippet-tags", value=tags_str, placeholder="タグをカンマ区切りで入力")

            abbr = self.data.get("abbr") or 0
            selection = [
                ("Abbr",              AbbrFlag.SIMPLE.value,            bool(abbr & AbbrFlag.SIMPLE)),
                ("Position Anywhere", AbbrFlag.POSITION_ANYWHERE.value, bool(abbr & AbbrFlag.POSITION_ANYWHERE)),
                ("Set Cursor",        AbbrFlag.SET_CURSOR.value,        bool(abbr & AbbrFlag.SET_CURSOR)),
            ]
            yield Label("[u]A[/u]bbr:")
            yield SelectionList(*selection, id="snippet-abbr")

    def action_focus_trig(self) -> None: self.query_one("#snippet-trigger").focus()
    def action_focus_body(self) -> None: self.query_one("#snippet-body").focus()
    def action_focus_memo(self) -> None: self.query_one("#snippet-memo").focus()
    def action_focus_tags(self) -> None: self.query_one("#snippet-tags").focus()
    def action_focus_abbr(self) -> None: self.query_one("#snippet-abbr").focus()


class SnippetApp(App):
    CSS = """
        SnippetEditor     { height: 1fr; width: 100%; }
        #button-container { height: 3; width: 100%; align: center middle; background: $panel; }
        Button            { margin: 0 1; }
    """
    BINDINGS = [
        ("alt+c", "focus_cncl"), ("alt+s", "focus_save"),
    ]

    def __init__(self, row_id, **kwargs):
        super().__init__(**kwargs)
        self.row_id = row_id

    def compose(self) -> ComposeResult:
        with get_db() as db:
            row = find_row(db, self.row_id)

        yield Header()
        with Vertical():
            yield SnippetEditor(row)
            yield Horizontal(
                Button("(C)キャンセル", variant="error", id="cancel-btn"),
                Button("(S)保存", variant="success", id="save-btn"),
                id="button-container"
            )

        yield Footer()

    def on_mount(self) -> None:
        """マウント時に実行される処理"""
        logger.debug("App mounted. Setting focus to #snippet-body")
        try:
            self.query_one("#snippet-body").focus()
        except Exception as e:
            logger.error(f"Focus error: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            raw_tags = self.query_one("#snippet-tags", Input).value
            tags_list = [t.strip() for t in raw_tags.split(",") if t.strip()]

            # Position/Cursor は abbr 有効が前提 (snippets.py と同じ補正)
            abbr = AbbrFlag(sum(self.query_one("#snippet-abbr", SelectionList).selected))
            if abbr:
                abbr |= AbbrFlag.SIMPLE

            updated_data = {
                "trigger": self.query_one("#snippet-trigger", Input).value,
                "body":    self.query_one("#snippet-body", TextArea).text,
                "memo":    self.query_one("#snippet-memo", TextArea).text,
                "tags":    tags_list,
                "abbr":    int(abbr),
            }
            logger.debug(f"save-btn pressed. data={updated_data}")

            with get_db() as db:
                db[C.TABLE].update(self.row_id, updated_data)

            self.notify(f"保存しました: {updated_data['trigger']}")
            self.exit()

        elif event.button.id == "cancel-btn":
            self.notify("キャンセルしました")
            self.exit()

    def action_focus_cncl(self) -> None: self.query_one("#cancel-btn").press()
    def action_focus_save(self) -> None: self.query_one("#save-btn").press()


if __name__ == "__main__":
    import sys
    SnippetApp(int(sys.argv[1])).run()
