#!/usr/bin/env bash
set -euo pipefail

mapfile -t tags < <(
  sqlite-utils rows ~/share/llogs.db snippets --json-cols --where 'mode IS NOT NULL' \
    | jq -r '.[].tags[]' | sort -u
)

for tag in "${tags[@]}"; do
  sqlite-utils rows ~/share/llogs.db snippets \
    --where "tags LIKE '%${tag}%'" --json-cols \
  | jq -r --arg TAG "$tag" '.[]
      | select(.tags[]? == $TAG)
      | (.mode // "t")    as $mode
      | (.body | [ scan("[0-9]+") ] | map(tonumber) | unique | sort) as $nums
      | ($nums | map("i(\(.))") | join(", ")) as $nodes
      | (
          if $mode == "fmta" then
            "  s(" + (.trigger| @json) + ", fmta([[" + .body + "]], { " + $nodes + " })),"
          elif $mode == "raw" then
            "  s(" + (.trigger| @json) + ", {" + .body + "}),"
          else
            "  s(" + (.trigger| @json) + ", t({" + (.body | split("\n") | map(@json) | join(", ")) + "})),"
          end
        )
  ' \
  | awk '
    BEGIN {
      print "local fmta = require(\"luasnip.extras.fmt\").fmta\n"
      print "return {"
    }
    { print }
    END {
      print "}"
    }
  ' > ~/.config/nvim/luasnippets/"${tag}".lua
done

