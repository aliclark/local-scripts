#!/bin/sh

if [ ! -x /usr/bin/emacs ]; then
    vim
    exit
fi

if [ "$TERM" = "screen" ]; then
    /usr/bin/emacs -nw $@
elif [ "$TERM" = "xterm" ]; then
    /usr/bin/emacs -nw $@
elif [ -n "$DISPLAY" ]; then
    xterm -e /usr/bin/emacs -nw $@
else
    /usr/bin/emacs $@
fi

