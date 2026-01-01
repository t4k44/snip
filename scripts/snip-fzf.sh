#!/bin/bash
# snip-fzf.sh

DB_FILE="${SNIP_DB_FILE:-$HOME/.config/snip/snippets.db}"
BAT_CMD="batcat" # または環境に合わせて変更

# 1. Python側は 'snip list --raw' でタブ区切りデータを出力するだけに専念
snip list --raw | fzf \
    --with-nth=2,3,4 --delimiter='\t' \
    --preview "sqlite3 $DB_FILE \"SELECT body || char(10) || '--------' || char(10) || memo FROM snippets
          WHERE id = {1}\" | $BAT_CMD -pl {5} --color=always" \
    --preview-window=right,50%,wrap \
    --bind "enter:accept" \
    --bind "ctrl-e:execute(sqlite-utils rows $DB_FILE snippets --where \"id={1}\" --nl --json-cols | 
          jq . > /tmp/snp_edit.json && nvim /tmp/snp_edit.json && 
          sqlite-utils upsert $DB_FILE snippets /tmp/snp_edit.json --pk id)" \
    --bind "ctrl-d:execute(sqlite-utils query $DB_FILE \"DELETE FROM snippets 
          WHERE id={1}\")+reload(snip list --raw)"
