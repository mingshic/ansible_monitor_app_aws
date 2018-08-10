#!/bin/bash 
METRIC="$1"
HOSTNAME={{ ansible_hostname  }}
PORT="${2:-6379}"
CACHE_FILE="/tmp/redis_$PORT.cache"

    (echo -en "INFO\r\n"; sleep 1;) | nc $HOSTNAME $PORT > $CACHE_FILE 2>/dev/null || exit 1

grep "^$METRIC:" $CACHE_FILE |awk -F':|,' '{print $2}'|sed "s/[^0-9.]//g"

if [ ${METRIC} == "maxmemory" ];then
        usedmem=`grep "^used_memory:" $CACHE_FILE |awk -F':|,' '{print $2}'|sed "s/[^0-9.]//g"`
        totalmem=`free -b | grep -E 'Mem' | awk '{print $2}'`
        if [ -f /data/apps/opt/redis/bin/redis-cli ];then
                maxmemeorysize=`sudo /data/apps/opt/redis/bin/redis-cli -h $HOSTNAME -p $PORT config get maxmemory| sed -n '2p'`
        elif [ -f /data/apps/opt/codis/bin/codis-cli ];then
                maxmemeorysize=`sudo /data/apps/opt/codis/bin/codis-cli -h $HOSTNAME -p $PORT config get maxmemory| sed -n '2p'`
        else
                maxmemeorysize="400"
        fi
        if [ ${maxmemeorysize} == "0" ];then
                echo "800"
        elif [ ${maxmemeorysize} == "400" ];then
                echo "400"
        else
                echo $(( ${maxmemeorysize} - ${usedmem} ))
        fi

fi
