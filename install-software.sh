#!/bin/bash

desired=(

flashplugin-nonfree

wine

emacs emacs-goodies-el

git-core
subversion

gambc
sbcl rlwrap
ghc

clang
gcc

)

# Manually install

# Dropbox

# Spotify

for package in ${desired[*]}
do
    # Use status code of this command to check if package is installed
    dpkg -s $package >/dev/null 2>&1
    # Do not put any commands in here, note $? will be trashed if you do.
    if [ $? != 0 ]
    then
        apt-get --yes install $package
    fi
done

