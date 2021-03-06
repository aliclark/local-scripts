#!/usr/bin/python

import sys
import datetime

s = None
t = None

def read_line():
    ts = datetime.datetime.now()
    s  = sys.stdin.readline()
    te = datetime.datetime.now()
    return (s, (te - ts))

while True:
    try:
        (s, t) = read_line()
        if len(s) == 0:
            break
        sys.stdout.write(str(t) + '| ' + s)
    except:
        break
