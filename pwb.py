#!/usr/bin/python

import string
from subprocess import *
import sys
import os

def split_branches(bl):
    lines = string.split(bl, '\n')
    others = []
    current = ''

    for l in lines:
        if not l:
            continue
        if l[0] == '*':
            current = l[2:]
        else:
            others.append(l[2:])

    return (others, current)

if not os.access("/usr/bin/git", os.X_OK):
    sys.exit(1)

proc = Popen(["/usr/bin/git", "branch"], stdout=PIPE, stderr=open('/dev/null', 'w'))
blist = proc.communicate()[0]

if proc.returncode == 0:
    (others, current) = split_branches(blist)
    print current
