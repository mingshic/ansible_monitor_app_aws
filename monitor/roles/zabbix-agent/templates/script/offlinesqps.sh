#!/bin/bash
if [ -f /data/apps/opt/kafkaMose/ejabberd-chat-offlines-AVER-QPS.data ];then
        num=`tail -1 /data/apps/opt/kafkaMose/ejabberd-chat-offlines-AVER-QPS.data | awk '{print $NF}'`
        if [ -z $num ];then
                echo "0"
        else
                echo $num
        fi

fi

