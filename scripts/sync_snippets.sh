#!/usr/bin/env bash
set -euo pipefail

DB="$HOME/.config/mine/snippets.db"
TAB="snippets"

# 1. CopyQ から JSON 形式で全アイテムを取得
# CopyQアイテムをJSON文字列で取得
ITEMS_JSON=$(copyq tab snippets eval -- '
var n = size();
print("[");
for (var i = 0; i < n; ++i) {
    var body = String(read(i))
        .replace(/\\/g, "\\\\")     // バックスラッシュ
        .replace(/"/g, "\\\"")      // ダブルクォート
        .replace(/\r/g, "\\r")      // CR
        .replace(/\n/g, "\\n")      // LF
        .replace(/\t/g, "\\t")      // TAB
        .replace(/[\u0000-\u001F]/g, function(c) {
            return "\\u" + ("000" + c.charCodeAt(0).toString(16)).slice(-4);
        });
    print("{ \"body\": \"" + body + "\" }");
    if (i < n - 1) print(",");
}
print("]\n");')

# 2. SQLite に登録
echo "$ITEMS_JSON" | tee /dev/tty | sqlite-utils insert $DB $TAB -

# ブランクの埋め
sqlite3 $DB <<EOF
  UPDATE $TAB
  SET trigger = 'memo', memo = '', tags = '["copyq"]', mode = 0
  WHERE trigger = '';
EOF

# 3. タブを初期化
copyq removetab snippets
