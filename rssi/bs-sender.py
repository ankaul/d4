#!/usr/bin/python

from scapy.all import *
from subprocess import check_output as co
import sys
import subprocess
import os
import re
import paho.mqtt.client as mqtt

NODE_ID = int(sys.argv[1])
NODE_NAME = 'enb%s' % NODE_ID
SCENARIO = sys.argv[2]
MQTT_SERVER = '192.168.0.1'
AP_MAC_LIST = ['00:00:00:00:00:01', '00:00:00:00:00:02', '00:00:00:00:00:03']
MAC_LIST = ['02:00:00:00:00:00', '02:00:00:00:02:00',
            '02:00:00:00:04:00', '02:00:00:00:06:00',
            '02:00:00:00:08:00', '02:00:00:00:0a:00',
            '02:00:00:00:0c:00', '02:00:00:00:0e:00',
            '02:00:00:00:10:00', '02:00:00:00:12:00']

UTIL_DIR = '~/mininet-wifi/util/m'
CMD = '{} enb{} iw dev enb{}-'.format(UTIL_DIR, NODE_ID, NODE_ID)
os.system('{}wlan1 interface add enb{}-mon1 type monitor'.format(CMD, NODE_ID))
os.system('ifconfig enb{}-mon1 up'.format(NODE_ID))
_decMatchRegex = re.compile( r'-\d+' )
TOPIC = ''
MSG = ''


def publish_mosq_car(mac, bssid, rssi, retain=''):
    cmd = '{} {} mosquitto_pub -h {} -t {} -m \"{},{}\" {}'.format(UTIL_DIR, NODE_NAME, MQTT_SERVER, mac, bssid, rssi, retain)
    os.system(cmd)


def publish_mosq_bs(bssid, load, retain=''):
    cmd = '{} {} mosquitto_pub -h {} -t {} -m {} {}'.format(UTIL_DIR, NODE_NAME, MQTT_SERVER, bssid, load, retain)
    os.system(cmd)


def mosquitto_subscribe(topic):
    return co('%s %s mosquitto_sub -h %s -t \"%s\" -C 1' % (UTIL_DIR, NODE_NAME, MQTT_SERVER, topic), shell=True)


def rssi_scenario(mac, rssi):
    global MSG
    global TOPIC
    cmd = '{} {} hostapd_cli -i enb{}-wlan1 sta {}'.format(UTIL_DIR, NODE_NAME, NODE_ID, mac)
    address = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    msg = out.decode('utf-8')
    bssid = AP_MAC_LIST[int(NODE_ID) - 1]
    if 'ASSOC' in msg:
        rssi = _decMatchRegex.findall(msg.split('\n')[21])[0]
        msg1 = '{},{},{}'.format(mac, bssid, rssi)
        print("Sending the following msg: %s" % msg1)
        publish_mosq_car(mac, bssid, rssi, retain='-r')
    else:
        TOPIC = mac
        client.connect(MQTT_SERVER, 1883, 1)
        #client.loop_forever()
        #client.loop_stop()
        bssid_ = MSG.split(',')
        if bssid != bssid_[0]:
            mac += '-target'
            msg1 = '{},{},{}'.format(mac, bssid, rssi)
            print("Sending the following msg: %s" % msg1)
            publish_mosq_car(mac, bssid, rssi, retain='-r')


def on_connect(client, userdata, flags, rc):
    global TOPIC
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    global MSG
    MSG = msg.payload.decode('utf-8')
    client.disconnect()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


def pkt_callback(pkt):
    if pkt.addr1 == 'ff:ff:ff:ff:ff:ff':
        mac = pkt.addr2
        rssi = pkt.dBm_AntSignal
        if SCENARIO == 'distributed':
            rssi_scenario(mac, rssi)


sniff(iface="enb%s-mon1" % NODE_ID,
      lfilter=lambda x: x.haslayer(Dot11ProbeReq),
      prn=pkt_callback, store=0)
