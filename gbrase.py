#!/usr/bin/python

import string
from subprocess import *
import sys
import os

def split_branches(bl):
    lines = string.split(bl, '\n')
    others = []
    current = None

    for l in lines:
        if not l:
            continue
        if l[0] == '*':
            current = l[2:]
        else:
            others.append(l[2:])

    if current == None:
        print 'eek could not find current branch!'
        sys.exit(1)

    return (others, current)

def runcmd(c):
    print 'SHELL: ' + c
    p = Popen(c, shell=True)
    sts = os.waitpid(p.pid, 0)[1]
    if sts != 0:
        print 'ERROR'
        sys.exit(sts)

blist = Popen(["git", "branch"], stdout=PIPE).communicate()[0]

(others, current) = split_branches(blist)


dopop = False
status = Popen(["git", "status", "-s"], stdout=PIPE).communicate()[0]

if status:
    print 'Please do a git stash'
    sys.exit(0)

    runcmd('git stash save')
    dopop = True

for o in others:
    runcmd('git checkout ' + o)
    runcmd('git-p4 rebase')

runcmd('git checkout ' + current)
runcmd('git-p4 rebase')

if dopop:
    runcmd('git stash pop')
