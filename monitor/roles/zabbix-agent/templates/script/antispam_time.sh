#/bin/bash
result=`java -jar /data/apps/opt/easemob-antispam/tools/client.jar {{ ansible_hostname  }} 9595 {{ appkey }} spam haha hehe test 2>/dev/null |awk '{print $4}'`
if [ -z $result ];then
	echo "0"
else
	echo $result
fi

