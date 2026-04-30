function snip_fzf --description "fzf selector for snip"
  argparse 't/tag=' -- $argv
  or begin
    echo "usage: "
    return 1
  end

  set -l tag_opt
  test -n "$_flag_tag"; and set tag_opt --tag $_flag_tag

  set -l selected (snip tui raw $tag_opt | sk \
    --with-nth=2,3,4 --delimiter='\t' \
    --preview "snip tui preview {1}" \
    --preview-window=right,50%,wrap \
    --bind "enter:accept" \
    --bind "ctrl-e:execute(snip tui edit   {1})+reload(snip tui raw)" \
    --bind "ctrl-d:execute(snip tui delete {1})+reload(snip tui raw)"
  )

  if test -n "$selected"
    set -l id (echo "$selected" | cut -f1)
    set -l body (snip tui get $id)
    commandline -i "$body"
  end
end
