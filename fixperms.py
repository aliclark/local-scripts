#!/usr/bin/python

import getopt
import os
import sys
import string
import stat
from subprocess import Popen, PIPE

recursive = False
hidden    = False
printc    = False
asExe     = False
files     = []

personal_file = stat.S_IRUSR | stat.S_IWUSR
personal_dir  = personal_file | stat.S_IXUSR
personal_exe  = personal_file | stat.S_IXUSR

public_file = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
public_dir  = public_file | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
public_exe  = public_file | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

perms_file = personal_file
perms_dir  = personal_dir
perms_exe  = personal_exe

try:
    options, xarguments = getopt.getopt(sys.argv[1:],
                                        'Ahr', ['recursive', 'almost-all', 'print', 'public', 'exe'])
except getopt.error:
    print 'Error: You tried to use an unknown option or the '
    'argument for an option that requires it was missing. Try '
    '\'-h\' for more information. '
    'sys.exit(0)'

for a in options[:]:
    if a[0] == '-h':
        print 'no help'
    elif a[0] == '--print':
        printc = True
    elif a[0] == '--public':
        perms_file = public_file
        perms_dir  = public_dir
        perms_exe  = public_exe
    elif a[0] == '--exe':
        asExe = True
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

    if origb == '':
        origb = os.path.dirname(orig)

    if origb[0] == '.' and (not hidden) and (not origb in ['.', '..']):
      continue

    if os.path.isdir(orig):
        perms = perms_dir
    else:
        if asExe:
            perms = perms_exe
        else:
            perms = perms_file

    stv = os.stat(orig)

    if perms != stat.S_IMODE(stv.st_mode):
        if printc:
            print "chmod " + str(perms) + " '" + orig + "'"
        else:
            os.chmod(orig, perms)

    if recursive and os.path.isdir(orig):
        subs = os.listdir(orig)
        for i in range(len(subs)):
            files.append(os.path.join(orig, subs[i]))

process()
