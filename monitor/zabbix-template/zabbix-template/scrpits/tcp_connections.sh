#!/bin/bash
#netstat -an | awk '/^tcp/ {++S[$NF]} END {for(a in S) print a, S[a]}' | grep $1 |awk '{print $$2}'
function SYNRECV {
num=`/usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'SYN-RECV' | awk '{print $2}'`
if [ -z $num ];then
        num=0
fi
echo $num
}
function ESTAB {
num=`/usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'ESTAB' | awk '{print $2}'`
if [ -z $num ];then
        num=0
fi
echo $num
}
function FINWAIT1 {
num=`/usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'FIN-WAIT-1' | awk '{print $2}'`
if [ -z $num ];then
        num=0
fi
echo $num
}
function FINWAIT2 {
num=`/usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'FIN-WAIT-2' | awk '{print $2}'`
if [ -z $num ];then
        num=0
fi
echo $num
}
function TIMEWAIT {
num=`/usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'TIME-WAIT' | awk '{print $2}'`
if [ -z $num ];then
        num=0
fi
echo $num
}
function LASTACK {
num=`/usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'LAST-ACK' | awk '{print $2}'`
if [ -z $num ];then
        num=0
fi
echo $num
}
function LISTEN {
num=`/usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'LISTEN' | awk '{print $2}'`
if [ -z $num ];then
        num=0
fi
echo $num
}
$1
