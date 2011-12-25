#!/usr/bin/python

import sys
import argparse

def base95(f, c, n, p):
  s = ''

  if p:
    pc = ' '
  else:
    pc = ''

  for i in range(n):
    while True:
      d = f.read((c - len(s)) * 3) # discard roughly 2/3
      s += ''.join(filter(lambda x: (ord(x) >= ord(' ')) and (ord(x) <= ord('~')), d))

      if len(s) >= c:
        print ''.join(map(lambda x: pc + x, s[:c]))
        s = s[c:]
        break

def base64(f, c, n, p):
  chars = ['+', '/']
  for i in range(26):
    chars.append(chr(ord('a') + i))
    chars.append(chr(ord('A') + i))
  for i in range(10):
    chars.append(chr(ord('0') + i))

  if p:
    pc = ' '
  else:
    pc = ''

  for i in range(n):
    print ''.join(map(lambda x: pc + chars[ord(x) & 63], f.read(c)))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--pad',   action='store_true', default=False)
  parser.add_argument('-c', '--bytes', type=int, default=12)
  parser.add_argument('-n', '--lines', type=int, default=1)
  parser.add_argument('-b', '--base',  type=int, default=95)

  args = parser.parse_args()

  if args.base != 95 and args.base != 64:
    print 'unknown base, use 64 or 95 (default)'
    sys.exit(1)

  f = open('/dev/random', 'rb')

  if args.base == 95:
    base95(f, args.bytes, args.lines, args.pad)

  if args.base == 64:
    base64(f, args.bytes, args.lines, args.pad)

  f.close()

if __name__ == '__main__':
  main()
