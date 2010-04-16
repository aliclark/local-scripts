#!/bin/bash

# User is advised to run `apt-get update` before this script
# and `apt-get autoclean`, `apt-get autoremove` after it.

# Written for debian squeeze

desired=(

vlc

vorbis-tools toolame sox ffmpeg gstreamer0.8-misc

lame lame-extras faad

w32codecs
libdvdcss2

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

# Add to /etc/apt/sources.list: deb http://www.debian-multimedia.org testing main non-free
# Needed for codecs
if [ `grep "debian-multimedia.org" /etc/apt/sources.list` == "" ]
then
    echo 'echo "deb http://www.debian-multimedia.org testing main non-free" >> /etc/apt/sources.list'
else
    echo 'multimedia entry present'
fi

# Check if packages exist, if not try to install them
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

# Manual install:

# Dropbox - todo, quite a long process here...

# Spotify
if [ ! -d ~/.wine/drive_c/Program\ Files/Spotify ]
then
    cd Desktop
    wget "http://www.spotify.com/download/Spotify%20Installer.exe"
    wine "./Spotify Installer.exe"
    rm -f "./Spotify Installer.exe"
fi
