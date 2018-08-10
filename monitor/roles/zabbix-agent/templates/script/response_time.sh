#!/bin/bash

TIME=`date -d "1 minutes ago"  +%F"T"%H:%M`
LOG="/data/apps/log/nginx/kefu.easemob.com.access.log"

if [ -f ${LOG} ];then

    if [ `tail -n50000 $LOG | grep -v 'GET /push'  | grep -v 'POST /push' | grep -c "$TIME"` -le 5 ];then
        echo "0.00"
        exit 0
    else
        tail -n50000 $LOG | grep -v 'GET /push'  | grep -v 'POST /push' | grep "$TIME" | awk '{print $NF}' | awk -F'|' '{print $1}' | awk '{sum+=$1} END {print  sum/NR}'
    fi

fi
