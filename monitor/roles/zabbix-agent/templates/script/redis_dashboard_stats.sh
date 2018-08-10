#!/bin/bash
HOST="$1"
if grep -E "$HOST" /tmp/redisdashboardlist >/dev/null 2>&1;then
        outtime=`grep -E "\b$HOST\b" /tmp/redisdashboardlist|awk '{print $(NF-1)}'|tail -1|sed "s/[^0-9.]//g"`
        if [ -z $outtime ];then
                echo "0"
        else
                echo $outtime
        fi

else

        echo "0"

fi
