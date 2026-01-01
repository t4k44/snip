# snip

`snip`は、スニペットを管理するためのコマンドラインツールです。`fzf`、`rofi`、`fish`、`nvim`、`skk`と連携してスニペットの追加、編集、検索、展開を効率的に行えます。

## Features

- **スニペットの追加・編集**: コマンドラインから簡単にスニペットを追加・更新できます。
- **FZF連携**: `fzf`を使ってインタラクティブにスニペットを検索し、選択したスニペットを標準出力に展開します。
- **Rofi連携**: `rofi`を使ってスニペットを選択し、クリップボードにコピー＆ペーストします。
- **Fish abbr連携**: Fish shellのabbr（略語）としてスニペットを自動生成します。
- **Neovim (LuaSnip)連携**: NeovimのLuaSnip形式でスニペットを自動生成します。
- **SKK連携**: SKKの辞書形式でスニペットを自動生成します。
- **SQLiteデータベース**: スニペットはSQLiteデータベースで管理されます。

## Installation

`pyproject.toml`に記載されている依存関係は以下の通りです。

- `argparse>=1.4.0`
- `sqlite-utils>=3.38`

これらの依存関係をインストールした後、`snip`をインストールしてください。

```bash
# uv を使用する場合
uv pip install .
# pip を使用する場合
pip install .
```

## Usage

### コマンドライン引数

```
usage: snip [-h] [--version] {list,add,edit} ...
```

### `list` コマンド

スニペットを一覧表示したり、各種ツール向けに出力します。

```
list mode:
  fzf   : commandline fzf selector `commandline -i (snip list fzf)` で呼び出し
  rofi  : launch rofi and snip to clipboard and paste
  fish  : output fish abbr          (path: ~/.config/fish/abbr.fish)
  nvim  : output luasnippets list   (path: ~/.config/nvim/luasnippets)
  skk   : output skk abbr           (path: ~/.config/ibus-skk/abbr.dict)
```

- `-t`, `--tag`: タグで絞り込みます。
- `mode`: `fzf`, `rofi`, `fish`, `nvim`, `skk` のいずれかを指定します。

例:
```bash
# fzfでスニペットを選択
commandline -i (snip list fzf)

# rofiでスニペットを選択し、クリップボードにペースト
snip list rofi

# fish abbrファイルを生成
snip list fish

# nvim luasnippetsファイルを生成
snip list nvim

# skk abbr辞書ファイルを生成
snip list skk
```

### `add` コマンド

新しいスニペットを追加します。

- `-t`, `--tags`: カンマ区切りのタグ（例: `python,cli`）。デフォルトは `fish`。
- `-m`, `--memo`: スニペットの説明。
- `-a`, `--abbr`: fish abbrのオプション。`1:ON / 2:Position / 4:SetCursor` の組み合わせ。
- `-c`, `--fish_cur_mark`: fish abbrのカーソル位置指定マーク。
- `-M`, `--mode`: nvimのモード。`t` (テキスト), `fmta` (タブストップ), `raw` (生)。
- `trigger`: スニペットのトリガー文字列。
- `body`: 展開される文字列。標準入力からも受け付けます。

例:
```bash
# 簡単なスニペットを追加
snip add my_snippet "Hello, world!" -t text -m "挨拶"

# 複数行のスニペットを標準入力から追加
echo "def func():\n    print('hello')" | snip add py_func -t python -m "Python関数"

# fish abbrとして追加
snip add -a 1 -c "%" fish_hello "echo Hello, %world!"
```

### `edit` コマンド

既存のスニペットを編集します。

- `-T`, `--trigger`: スニペットのトリガー文字列。
- `-b`, `--body`: 展開される文字列。
- `id`: 更新対象のスニペットID。
- その他のオプションは `add` コマンドと同様です。

例:
```bash
# ID 123のスニペットのbodyを更新
snip edit 123 -b "Updated body content"

# ID 456のスニペットのタグを更新
snip edit 456 -t "python,new_tag"
```

## Development

### ファイル構成

- `src/snip/main.py`: メインのCLIエントリポイント。引数解析とコマンドディスパッチを行います。
- `src/snip/constants.py`: データベースのテーブル名、ファイルパス、クリップボードコマンドなどの定数を定義します。
- `src/snip/snippets.py`: スニペットの追加、更新などのデータベース操作を処理します。
- `src/snip/snip_list.py`: `fzf`と`rofi`を使ったスニペットの選択と表示ロジックを実装します。
- `src/snip/fish_abbr.py`: Fish shellのabbrファイルを生成します。
- `src/snip/nvim.py`: NeovimのLuaSnipファイルを生成します。
- `src/snip/skk.py`: SKKのabbr辞書ファイルを生成します。

## License

[LICENSE](LICENSE) (もしあれば)
