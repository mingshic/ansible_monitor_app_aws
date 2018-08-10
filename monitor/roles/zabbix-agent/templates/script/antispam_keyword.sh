#/bin/bash
if [ -f "/data/apps/opt/easemob-textparse/tools/keyword.jar" ];then
#        result=`cd /data/apps/opt/easemob-textparse/tools;java -jar keyword.jar vip5-ali-hangzhou-antispam1 8090 test moer#moer 15116447530 2>/dev/null | grep -Ei 'ResultMessage'`
        result=`cd /data/apps/opt/easemob-textparse/tools;java -jar keyword.jar {{ ansible_hostname  }} 8090 test {{ appkey }} 15116447530 2>/dev/null | grep -Ei 'ResultMessage'`
        if [ -z "$result" ];then
                echo "0"
        else
                echo "1"
        fi

else
        echo 2
fi
