#!/bin/sh

fname=$1

bibtex $fname && fixtexcount.sh $fname.tex && fixtexdate.sh $fname.tex && pdflatex $fname && pdflatex $fname && cp $fname.pdf ~/web
