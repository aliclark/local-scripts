#!/bin/sh

apt-get update
apt-get --yes dist-upgrade
apt-get --yes autoremove
apt-get --yes autoclean
