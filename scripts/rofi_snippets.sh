#!/usr/bin/env bash

DB="$HOME/share/llogs.db"
LENGTH=40   # body/memo の表示長さ
TMPFILE="$(mktemp).sh"

case "$ROFI_RETV" in
  0)   # 一覧フェーズ
    sqlite3 -json "$DB" "
      select id, trigger, tags,
        replace(substr(body, 0, $LENGTH), char(10), '↩') AS body,
        replace(substr(coalesce(memo, ''), 0, $LENGTH), char(10), '↩') as memo
      from snippets order by id desc" \
    | jq -r '.[] | "\(.id)\t\(.trigger)\t\(.body)\t\(.tags)\t\(.memo)"'
    ;;
  1)    # 選択後フェーズ
    line="$1"

    id=$(echo "$line" | cut -f1)
    sqlite3 -json "$DB" "select body from snippets where id=$id" | jq -r '.[0].body' > $TMPFILE

    # Alacritty を新規起動して body を貼り付け
    (alacritty -e bash -c "
      vim  $TMPFILE
      fish $TMPFILE
    ") >> /tmp/snippet.log 2>&1 &
    ;;
esac
