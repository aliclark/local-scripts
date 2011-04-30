#!/usr/bin/python

import getopt
import os
import sys
import string
from subprocess import Popen, PIPE

command   = 'mv'
recursive = False
hidden    = False
printc    = False
files     = []

try:
    options, xarguments = getopt.getopt(sys.argv[1:],
                                        'Ahr', ['command=', 'recursive', 'almost-all', 'print'])
except getopt.error:
    print 'Error: You tried to use an unknown option or the '
    'argument for an option that requires it was missing. Try '
    '\'-h\' for more information. '
    'sys.exit(0)'

for a in options[:]:
    if a[0] == '-h':
        print 'no help'
    elif a[0] == '--command':
        command = a[1]
    elif a[0] == '--print':
        printc = True
    elif a[0] in ['--almost-all', '-A']:
        hidden = True
    elif a[0] in ['--recursive', '-r']:
        recursive = True

for a in xarguments:
  files.append(a)

def process():
  global files

  while len(files) != 0:
    orig = files.pop()
    origb = os.path.basename(orig)
    origd = os.path.dirname(orig)

    if origb == '':
        origb = origd
        origd = ''

    if origb[0] == '.' and (not hidden) and (not origb in ['.', '..']):
      continue

    t1 = origb
    f  = origb
    doloop = True
    while doloop or f != t1:
        doloop = False
        t1 = f
        f = f.replace(' ', '-').replace(',', '-').replace('(', '-').replace(')', '-').replace('--', '-').replace('_', '-')
        f = string.lower(f).replace("'", '').replace('"', '').replace('-.', '.').replace('!', '').replace('\n', '')
        f = f.replace('\xe2\x80\x99', '')

    newf = os.path.join(origd, f)

    if f != origb:
      if os.path.exists(f):
        print 'Warning, path ' + newf + ' already exists'
      else:
        if printc:
          print " '" + orig + "' '" + newf + "'"
        else:
          Popen([command, orig, newf], stdout=PIPE).communicate()[0]

    if printc:
      innr = orig
    else:
      innr = newf

    if recursive and os.path.isdir(innr):
        subs = os.listdir(innr)
        for i in range(len(subs)):
          files.append(os.path.join(innr, subs[i]))

process()
