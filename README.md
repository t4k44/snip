# snip

`snip`は、スニペットを管理するためのコマンドラインツールです。`fzf`、`rofi`、`fish`、`nvim`、`skk`と連携してスニペットの追加、編集、検索、展開を効率的に行えます。

## Features

- **スニペットの追加・編集**: コマンドラインから簡単にスニペットを追加・更新できます。
- **FZF連携**: `fzf`を使ってインタラクティブにスニペットを検索し、選択したスニペットを標準出力に展開します。
    - [ ] scripts/snip_fzf.fish の説明
- **Rofi連携**: `rofi`を使ってスニペットを選択し、クリップボード経由でコピー＆ペーストします。
- **fish abbr連携**: fish shellのabbr（略語）としてスニペットを自動生成します。
- **Neovim (LuaSnip)連携**: NeovimのLuaSnip形式でスニペットを自動生成します。
- **SKK連携**: SKKの辞書形式でスニペットを自動生成します。
- **SQLiteデータベース**: スニペットはSQLiteデータベースで管理されます。

## Installation

```bash
git clone git@github.com:t4k44/snip.git
cd snip
uv tool install .
```

## Usage

### `snip` (基本コマンド)

```bash
# スニペットの追加 (引数または標準入力)
snip add trigger_name "body content" -t tag1,tag2 -m "memo"
echo "multiline body" | snip add trigger_name -t tag1

# スニペットの編集 (ID指定)
snip edit 123 --body "new body" --tags new_tag

# スニペットの削除
snip delete 123
```

### `list` コマンド

スニペットを一覧表示したり、fish abbrを生成したりします。

```bash
# 指定したタグのチートシートを表示
snip list cheat-sheet my_tag    # 短縮形 cs

# fish shell の略語 (abbr) ファイルを生成
snip list fish
```

### `tui` コマンド (fzf/sk等との連携用)

TUIセレクタ（`fzf`や`sk`）から呼び出すための低レベルコマンドです。

```bash
# fzfに渡すためのタブ区切り一覧を出力
snip tui list TAG

# 指定IDのスニペットのプレビューを表示
snip tui preview 123

# 指定IDのスニペット本文を取得 (使用回数カウントアップ)
snip tui get 123

# 指定IDのスニペット本文を編集
snip tui edit 123
```

### `gui` コマンド

```bash
# Rofiを起動してスニペットを選択し、クリップボードにコピー＆ペースト
snip gui my_tag
```

## Development

### ファイル構成

- `src/snip/main.py`: CLIのエントリポイント（Typer）。
- `src/snip/snippets.py`: `add`, `edit`, `delete` コマンドの実装。
- `src/snip/list.py`: `list cs`, `list fish` コマンドの実装。
- `src/snip/tui.py`: `fzf`連携用のサブコマンド群。
- `src/snip/gui.py`: `rofi`連携用のサブコマンド。
- `src/snip/utils.py`: 共通のユーティリティ関数。
- `src/snip/constants.py`: パスやDB構成の定義。

### Testing

`pytest` を使用してテストを実行します。

```bash
# 全てのテストを実行
uv run pytest

# カバレッジを表示
uv run pytest --cov=src --cov-report=term-missing

# lint check
uv run ruff check --fix
```

テスト環境ではインメモリDBを使用し、実際のファイルやデータベースを書き換えることなく動作を確認できます。

## License

[LICENSE](LICENSE)
