#!/bin/sh

dd if=/dev/urandom of=$1/.urandomfile
rm -f $1/.urandomfile
