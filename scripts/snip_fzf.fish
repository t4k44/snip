function snip_fzf --description 'fzf selector for snip'
    _debug_log "[snip_fzf] START: argv=$argv"
    set -l tmp_key (mktemp)   # キー情報を保存する一時ファイル
    _debug_log "[snip_fzf] Created tmp_key=$tmp_key"

    # execute-silent を使用してキーバインドの横取りを防止
    set -l selected_line (snip tui list $argv | sk \
                --header "Enter: get / Ctrl-e: edit / Ctrl-d: delete" \
                --with-nth=2,3,4 --delimiter='\t' \
                --preview "snip tui preview {1}" \
                --preview-window=right,50%,wrap \
                --bind "ctrl-e:execute-silent(echo edit > $tmp_key)+accept" \
                --bind "ctrl-d:execute-silent(echo delete > $tmp_key)+accept" \
              )
    set -l sk_status $status
    _debug_log "[snip_fzf] sk finished: sk_status=$sk_status, selected_line='$selected_line'"

    if test $sk_status -ne 0 -a $sk_status -ne 1 # sk 自体がキャンセルされた場合
        _debug_log "[snip_fzf] STOP: Canceled by sk (sk_status=$sk_status). Cleaning up tmp_key."
        rm -f $tmp_key
        return
    end

    set -l action (string trim (cat $tmp_key))    # キー情報をファイルから読み取る（空なら Enter）
    test -z "$action"; and set action "get"
    _debug_log "[snip_fzf] Read action='$action'"
    rm -f $tmp_key

    # IDの抽出
    set -l trimmed_line (string trim "$selected_line")
    set -l id (string match -r '^[0-9]+' -- "$trimmed_line")
    _debug_log "[snip_fzf] Extracting ID: trimmed_line='$trimmed_line', id='$id'"

    if test -z "$id"
        _debug_log "[snip_fzf] STOP: Failed to extract ID from selected line."
        return
    end

    # アクションの実行
    _debug_log "[snip_fzf] Executing switch-case for action='$action' with id='$id'"
    switch $action
        case edit
            _debug_log "[snip_fzf] BEFORE EXEC: Running 'snip tui edit $id'"
            snip tui edit $id
            _debug_log "[snip_fzf] RECURSION: Calling snip_fzf after edit"
            snip_fzf
        case delete
            _debug_log "[snip_fzf] BEFORE EXEC: Running 'snip delete $id'"
            snip delete $id
            _debug_log "[snip_fzf] RECURSION: Calling snip_fzf after delete"
            snip_fzf
        case get
            _debug_log "[snip_fzf] BEFORE EXEC: Running 'snip tui get $id'"
            set -l body (snip tui get $id)
            _debug_log "[snip_fzf] Inserting body to commandline: body='$body'"
            commandline -i "$body"
        case '*'
            _debug_log "[snip_fzf] STOP: Unknown action '$action'"
    end
end
