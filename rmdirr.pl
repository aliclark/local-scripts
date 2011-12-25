#!/usr/bin/env perl

use File::Find;

finddepth( sub{rmdir}, ($#ARGV == -1) ? '.' : $ARGV[0]);

