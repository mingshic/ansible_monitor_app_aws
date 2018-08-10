#!/bin/bash
METRIC="$1"
HOSTNAME=${2:-ebs-ali-beijing-msync1}
COOKIE="${3:-EASEMOBAAAAAAAAAAEBS}"
CACHE_FILE="/tmp/msync_cache"
cd /data/shell/erl_tool/ && /data/shell/erl_tool/erl_expect -echo -sname msync@${HOSTNAME} -setcookie ${COOKIE} msync/health.erl > $CACHE_FILE 2>/dev/null || exit 1
grep "^$METRIC:" $CACHE_FILE |awk -F':|,' '{print $2}'|sed "s/[^0-9].//g"
