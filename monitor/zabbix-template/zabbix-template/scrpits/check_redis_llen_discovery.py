#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import json
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Check redis topic llen\n')
    parser.add_argument('-f', '--file', help='redis topic config file\n', required=True)
    args =  parser.parse_args()

    topic_file = args.file

    fp = open(topic_file,'r')
    data = list()
    for line in fp.readlines():
        if line:
            linedata = line.split()
            data.append({"{#LLEN_HOST}": linedata[0], "{#LLEN_PORT}": linedata[1], "{#LLEN_TOPIC}": linedata[2]})

    print(json.dumps({"data": data}, indent=4))

