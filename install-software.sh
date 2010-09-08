#!/bin/bash

# User is advised to run `apt-get update` before this script
# and `apt-get autoclean`, `apt-get autoremove` after it.

# Written for debian squeeze

desired=(

# Video playback
vlc

# Codecs
vorbis-tools toolame sox ffmpeg

lame faad

w32codecs
libdvdcss2

youtube-dl

# Font
msttcorefonts

# Flash
flashplugin-nonfree

# Windows applications
wine

# Text editing
emacs emacs-goodies-el

# Revision control
git-core
subversion

# Interpreted languages
gambc
sbcl rlwrap
ghc

# C compilers
clang
gcc

gdb
valgrind

# Because I will inevitably want to change my partitions
gparted

ntpdate

#tor privoxy

htop

nmap netcat tcpdump

)

# Add to /etc/apt/sources.list: deb http://www.debian-multimedia.org testing main non-free
# Needed for codecs
if [ "$(grep 'debian-multimedia.org' /etc/apt/sources.list)" == "" ]
then
    echo "deb http://www.debian-multimedia.org testing main non-free" >> /etc/apt/sources.list
fi

# Check if packages exist, if not try to install them
for package in ${desired[*]}
do
    # If not installed
    if ! dpkg -s $package > /dev/null 2>&1
    then
        apt-get --yes install $package
    fi
done

# Manual install:

# Skype

# Dropbox - todo, quite a long process here...

# Spotify
if [ ! -d ~/.wine/drive_c/Program\ Files/Spotify ]
then
    cd Desktop
    wget "http://www.spotify.com/download/Spotify%20Installer.exe"
    wine "./Spotify Installer.exe"
    rm -f "./Spotify Installer.exe"
fi

# NoMachine
