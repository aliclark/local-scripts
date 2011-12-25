#!/bin/sh

hour=`date "+%H"`

if [ "$hour" -lt "8" ]; then
    colour='ff0000'
elif [ "$hour" -gt "21" ]; then
    colour='ee9a00'
elif [ "$hour" -lt "9" ]; then
    colour='ee9a00'
else
    colour='00ff00'
fi

echo "<fc=#$colour>`date \"+%H:%M %a %d %b\"`</fc>"

