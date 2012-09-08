#!/bin/sh

editor=vi

# Must be checking at /usr/bin not /usr/local/bin
[ -x /usr/bin/vim ] && editor=vim

if [ "$TERM" = "screen" ]; then
    /usr/bin/$editor $@
elif [ "$TERM" = "xterm" ]; then
    /usr/bin/$editor $@
elif [ -n "$DISPLAY" ]; then
    xterm -e /usr/bin/$editor $@
else
    # change this to gvim
    /usr/bin/$editor $@
fi

