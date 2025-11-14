sqlite-utils rows ~/share/llogs.db snippets -ctrigger -cbody -cmemo -cabbr -ctags -cmode | sqlite-utils insert snippets.db snippets - --pk=id
