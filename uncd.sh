#!/bin/sh

dir=`basename $1`
dirfile=$HOME/.stagingdir

if [ -f $dirfile ]; then
  stagingdir=`cat $HOME/.stagingdir`
else
  stagingdir=$HOME/.staging
fi

if [ ! -f $stagingdir/crypt/$dir.key.gpg ]; then
  echo 'No such folder'
  exit
fi

fusermount -u $HOME/$dir
rmdir $HOME/$dir

