#!/bin/bash

if [[ $# = 0 ]]; then
    numc=12
else
    numc=$1
fi

</dev/urandom tr -dc A-HJ-NP-Za-hj-np-z2-9 | /usr/bin/head -c $numc
echo
