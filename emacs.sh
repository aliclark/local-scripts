#!/bin/sh

if [ "$TERM" = "screen" ]; then
    /usr/bin/emacs -nw $@
elif [ "$TERM" = "xterm" ]; then
    /usr/bin/emacs -nw $@
elif [ -n "$DISPLAY" ]; then
    xterm -e /usr/bin/emacs -nw $@
else
    /usr/bin/emacs $@
fi

