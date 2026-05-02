function snip_fzf --description "fzf selector for snip"
  set -l tmp_key (mktemp)   # キー情報を保存する一時ファイル

  set -l selected_line (snip tui list $argv | sk \
    --header "Enter: get / Ctrl-e: edit / Ctrl-d: delete" \
    --with-nth=2,3,4 --delimiter='\t' \
    --preview "snip tui preview {1}" \
    --preview-window=right,50%,wrap \
    --bind "enter:accept" \
    --bind "ctrl-e:execute(echo edit   > $tmp_key)+accept" \
    --bind "ctrl-d:execute(echo delete > $tmp_key)+accept" \
  )

  if test $status -ne 0 -a $status -ne 1 # sk 自体がキャンセルされた場合
    rm -f $tmp_key
    return
  end

  set -l action (cat $tmp_key)    # キー情報をファイルから読み取る（空なら Enter）
  test -z "$action"; and set action "get"
  rm -f $tmp_key

  # IDの抽出
  set -l id (string match -r '^[0-9]+' -- (string trim "$selected_line"))
  test -z "$id"; and return

  # skが終了した後に実行
  switch $action
    case edit
      uv run snip tui edit $id
      snip_fzf
    case delete
      echo uv run snip tui delete $id
      snip_fzf
    case get
      set -l body (snip tui get $id)
      commandline -i "$body"
  end
end
