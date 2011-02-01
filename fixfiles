#!/bin/bash

for f in ./*; do
    ext=`echo "$f" | awk -F . '{if (NF>1) {print $NF}}'`

    case $ext in
        'pdf' )
            echo "fixing pdf $f"
            pdftotext $f
            ;;
        'xls' )
            echo "fixing xls $f"
            xls2csv $f > "`basename $f $ext`csv"
            ;;
        'ppt' )
            echo "fixing ppt $f"
            ppthtml $f > "`basename $f $ext`html"
            ;;
        * )
            ;;
    esac

done
