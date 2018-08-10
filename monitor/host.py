#!/usr/bin/python 
import string
import os
import socket 
import struct 
import fcntl 

def getip(ethname): 
	s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0X8915, struct.pack('256s',ethname[:15]))[20:24]) 


def choise_card():
	eth = netifaces.gateways()['default'][netifaces.AF_INET][1]
	return eth
	 	
if __name__=='__main__': 	
	try:
    		import netifaces
	except ImportError:
                try:
			command_to_execute = "pip install netifaces || easy_install netifaces"
			os.system(command_to_execute)
		except OSError:
			print "Can NOT install netifaces, Aborted!"
			sys.exit(1)
		import netifaces
	IP_eth = choise_card()
	IP = getip(str(IP_eth))
	print IP
