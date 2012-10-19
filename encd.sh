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

if [ -d $HOME/$dir ]; then
  echo "$dir already exists"
  exit
fi

mkdir $HOME/$dir
cd $HOME && gpg -d $stagingdir/crypt/$dir.key.gpg | encfs -S -o allow_root $stagingdir/crypt/${dir}_encfs $HOME/$dir

