#!/usr/bin/python

from scapy.all import *
import sys
import os
import socket
from datetime import datetime


NODE_ID = int(sys.argv[1])
SCENARIO = sys.argv[2]
DELAYED = sys.argv[3]
host_ip = '172.210.0.1'
MAC_LIST = ['02:00:00:00:00:00', '02:00:00:00:02:00',
            '02:00:00:00:04:00', '02:00:00:00:06:00',
            '02:00:00:00:08:00', '02:00:00:00:0a:00',
            '02:00:00:00:0c:00', '02:00:00:00:0e:00',
            '02:00:00:00:10:00', '02:00:00:00:12:00']


def setEmergencyMsg():
    host = host_ip
    port = 12345  # Make sure it's within the > 1024 $$ <65535 range
    s = socket.socket()
    s.connect((host, port))
    msg = "set.car%s.sumo.stop" % NODE_ID
    print('Sending %s to Mininet-WiFi:' % msg)
    # stop can be replaced with resume and setRouteID
    s.send(str(msg).encode('utf-8'))
    data = s.recv(1024).decode('utf-8')
    print('Received from server: ' + data)
    s.close()


def mosquitto_publish(topic, bssid):
    cmd = 'mosquitto_pub -h 192.168.254.200 -t {} -m {} -r'.format(topic, bssid)
    print(cmd)
    msgTime = 'Vehicle: message was sent when T=%s' % datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    if int(float(DELAYED)) != 1000:
        os.system('echo \"%s\" >> %s' % (msgTime, 'timestamp-%s-delayed.txt' % SCENARIO))
    else:
        os.system('echo \"%s\" >> %s' % (msgTime, 'timestamp-%s.txt' % SCENARIO))
    os.system('echo \"%s\" >> %s' % (msgTime, 'timestamp.txt'))
    os.system(cmd)


if __name__ == '__main__':
    topic = MAC_LIST[int(NODE_ID) - 1] + '-emergency'
    mosquitto_publish(topic, 'accident')
