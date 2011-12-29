#!/bin/sh

if [ "$TERM" = "screen" ]; then
    /usr/bin/vim $@
elif [ "$TERM" = "xterm" ]; then
    /usr/bin/vim $@
elif [ -n "$DISPLAY" ]; then
    xterm -e /usr/bin/vim $@
else
    # change this to gvim
    /usr/bin/vim $@
fi

