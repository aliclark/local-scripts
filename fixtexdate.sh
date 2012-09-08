#!/bin/sh

sed -i "s/^\\\date{Version \\(.*\\), .*}$/\\\date{Version \\1, `date '+%Y-%B-%d'`}/" $1
