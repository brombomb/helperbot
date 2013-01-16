#!/bin/sh
SERVICE='10100bot'
 
 if ps ax | grep -v grep | grep $SERVICE > /dev/null
    then
        echo "$SERVICE service running, everything is fine"
    else
        python /home/brombomb/www/site/10100bot/10100bot.py& > /home/brombomb/www/site/10100bot/status.txt
fi
