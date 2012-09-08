#!/usr/bin/python

from __future__ import print_function

import sys
# TODO: use more widely available alternative eg. getopt
#import argparse
import math

rand_stream = None

def xrand_stream_nb(b):
  global rand_stream

  savedn = 0
  savedv = 0
  x = None
  y = 0
  mask = (2 ** b) - 1

  while True:
    while savedn >= b:
      y = savedv & mask
      savedv >>= b
      savedn  -= b
      yield y

    if rand_stream == None:
      rand_stream = open('/dev/random', 'rb')

    try:
      x = rand_stream.read(int(math.ceil((b - savedn) / 8.)))
    except:
      x = ''

    if len(x) == 0:
      try:
        rand_stream.close()
      finally:
        rand_stream = None
        raise EOFError('EOS')

    while len(x) >= 1:
      savedv <<= 8
      savedv |= ord(x[0])
      savedn += 8
      x = x[1:]

def xrand_stream_n(l, t=None):
  if t == None:
    t = l
    l = 0

  if t <= l:
    return

  n = t - l
  i = 0
  while 2**i < n:
    i += 1

  s = xrand_stream_nb(i)
  for x in s:
    if x < n:
      yield x + l

def base(b, c, n=1, p=False):
  txt = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/!\"#$%&'()*,-.:;<=>?@[\\]^_`{|}~ "
  s = xrand_stream_n(b)
  pc = ' ' if p else ''
  for i in xrange(n):
    for j in xrange(c):
      try:
        sys.stdout.write(pc + txt[s.next()])
        sys.stdout.flush()
      except:
        break

    sys.stdout.write('\n')
    sys.stdout.flush()

class mkargs(object):
  def __init__(self):
    self.pad = False
    self.bytes = 48 #32
    self.lines = 1
    #self.base = 64
    self.base = 95

def main():
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--pad',   action='store_true', default=False)
  parser.add_argument('-c', '--bytes', type=int, default=12)
  parser.add_argument('-n', '--lines', type=int, default=1)
  parser.add_argument('-b', '--base',  type=int, default=95)

  args = parser.parse_args()
  """

  args = mkargs()

  if args.base < 0:
    print('minimum base is 0')
    sys.exit(1)

  if args.base > 95:
    print('maximum base is 95')
    sys.exit(1)

  base(args.base, args.bytes, args.lines, args.pad)

if __name__ == '__main__':
  main()
