#!/bin/sh

sed -i "s/^\\\wordcount{.*}$/\\\wordcount{`texcount $1 | grep 'Words in text:' | cut -c16-`}/" $1
