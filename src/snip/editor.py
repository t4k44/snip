import json

from pyutils.logger import setup_logger
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, Label, SelectionList, Static, TextArea

import snip.constants as C
from snip.utils import get_db

logging = setup_logger(__name__)

class SnippetEditor(Static):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        logging.debug(f"SnippetEditor.__init__: initial_data={self.data}")

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("[u]T[/u]rigger:")
            yield Input(id="snippet-trigger", value=self.data.get("trigger"))

            yield Label("[u]B[/u]ody:")
            yield TextArea(id="snippet-body", text=self.data.get("body"))

            yield Label("[u]M[/u]emo:")
            yield TextArea(id="snippet-memo", text=self.data.get("memo", ""))

            raw_tags = self.data.get("tags")
            try:
                tags_list = json.loads(raw_tags) if raw_tags else []
                tags_str = ','.join(tags_list)
            except (json.JSONDecodeError, TypeError):
                tags_str = ""
            yield Label("Ta[u]g[/u]s:")
            yield Input(id="snippet-tags", value=tags_str, placeholder="タグをカンマ区切りで入力")

            abbr = self.data.get("abbr")
            selection = [
                ("Abbr",              1, bool(abbr & 1)),
                ("Position Anywhere", 2, bool(abbr & 2)),
                ("Set Cursor",        4, bool(abbr & 4)),
            ]
            yield Label("[u]A[/u]bbr:")
            yield SelectionList(*selection, id="snippet-abbr")

    BINDINGS = [
        ("alt+t", "focus_trig"),
        ("alt+b", "focus_body"),
        ("alt+m", "focus_memo"),
        ("alt+g", "focus_tags"),
        ("alt+a", "focus_abbr"),
    ]
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

    def __init__(self, id, **kwargs):
        super().__init__(**kwargs)
        self.row_id = id


    def compose(self) -> ComposeResult:
        with get_db() as db:
            row = db[C.TABLE].get(self.row_id)

        yield Header()
        with Vertical():
            yield SnippetEditor(row)
            yield Horizontal(
                Button("キャンセル", variant="error", id="cancel-btn"),
                Button("保存", variant="success", id="save-btn"),
                id="button-container"
        )

        yield Footer()


    def on_mount(self) -> None:
        """マウント時に実行される処理"""
        logging.debug("App mounted. Setting focus to #snippet-trigger")
        try:
            self.query_one("#snippet-body").focus()
        except Exception as e:
            print(f"Focus error: {e}")


    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            raw_tags = self.query_one("#snippet-tags", Input).value
            tags_list = [t.strip() for t in raw_tags.split(",") if t.strip()]

            updated_data = {
                "id":      self.row_id,
                "trigger": self.query_one("#snippet-trigger").value,
                "body":    self.query_one("#snippet-body").text,
                "memo":    self.query_one("#snippet-memo").text,
                "tags":    tags_list,
                "abbr":    sum(self.query_one("#snippet-abbr", SelectionList).selected),
            }
            logging.debug(f"save-btn pressed. data={updated_data}")

            with get_db() as db:
                db[C.TABLE].upsert(updated_data, pk="id")


            self.notify(f"保存しました: {updated_data["trigger"]}")
            self.exit()

        if event.button.id == "cancel-btn":
            self.notify("キャンセルしました")
            self.exit()

if __name__ == "__main__":
    import sys
    app = SnippetApp(sys.argv[1])
    app.run()
