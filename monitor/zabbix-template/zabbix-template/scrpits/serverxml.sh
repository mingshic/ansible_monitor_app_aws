#!/bin/bash
#http://www.easemob.com/easemob/server.xml
#http://rs.easemob.com/easemob/server.xml

function server {
time=`curl -s -o /dev/null --connect-timeout 10 -w %{time_total} http://www.easemob.com/easemob/server.xml`
if [ -z $time ];then
        time=0
fi
echo $time
}

function server_rs {
time=`curl -s -o /dev/null --connect-timeout 10 -w %{time_total} http://rs.easemob.com/easemob/server.xml`
if [ -z $time ];then
        time=0
fi
echo $time
}

$1
