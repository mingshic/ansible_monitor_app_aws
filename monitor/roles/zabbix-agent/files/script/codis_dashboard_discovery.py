#!/usr/bin/python
# -*- coding: utf-8 -*-
# --author: hanyn@easemob.com --

import os
import json
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Check codis dashboard ops\n')
    parser.add_argument('-f', '--file', help='codis dashboard config file\n', required=True)
    args =  parser.parse_args()

    config_file = args.file

    fp = open(config_file,'r')
    data = list()
    for line in fp.readlines():
        if line:
            linedata = line.strip()
            #print linedata
            data.append({"{#DASHBOARD_IP}": linedata})

    print(json.dumps({"data": data}, indent=4))
