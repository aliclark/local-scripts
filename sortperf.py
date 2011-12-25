#!/usr/bin/python

import sys

lines = []
i = 0

while True:
    try:
        s = sys.stdin.readline()
        if len(s) == 0:
            break

        sys.stdout.write(str(i).ljust(3) + ' ' + s)

        lines.append((float(s[6:14]), s[16:-1], s))

        i+=1
    except:
        break

print '-----------------------------------------------------------------'

def diffkey(x):
    return lines[x][0]

maxLines = 30
n = 0

for y in sorted([x for x in xrange(len(lines))], key=diffkey, reverse=True):
    if n == maxLines:
        break
    n += 1

    if y == 0:
        print '<start>'
    else:
        sys.stdout.write(str(y - 1).ljust(3) + ' ' + lines[y - 1][2])

    sys.stdout.write(str(y).ljust(3) + ' ' + lines[y][2])

    print '-------------------------------'



