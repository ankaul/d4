#!/usr/bin/python

from scapy.all import *
import sys
import os
import subprocess
from subprocess import check_output as co
from time import sleep
import paho.mqtt.client as mqtt


NODE_ID = int(sys.argv[1])

MININET_WIFI_DIR = '~/mininet-wifi/util/m'
MAC_LIST = ['02:00:00:00:01:00', '02:00:00:00:03:00',
            '02:00:00:00:05:00', '02:00:00:00:07:00',
            '02:00:00:00:09:00', '02:00:00:00:0b:00',
            '02:00:00:00:0d:00', '02:00:00:00:0f:00',
            '02:00:00:00:11:00', '02:00:00:00:13:00']
MAC_NODE = MAC_LIST[int(NODE_ID)-1]
MQTT_SERVER = '192.168.254.200'
TOPIC = ''
MSG = ''

neigh = None
target_neigh = None
neigh_rssi = -200
target_neigh_rssi = -200


def get_neighbor():
    cmd = ["%s car%s route -n | awk '{print $2}'" % (MININET_WIFI_DIR, NODE_ID)]
    address = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    dest = str(out).split('\n')
    return dest


def mosquitto_publish(topic, bssid):
    cmd = 'mosquitto_pub -h {} -t {} -m {} -r'.format(MQTT_SERVER, topic, bssid)
    os.system(cmd)


def mosquitto_subscribe(topic):
    cmd = 'mosquitto_sub -h {} -t {} -C 1'.format(MQTT_SERVER, topic)
    return co(cmd, shell=True)


def pkt_callback_adhoc(pkt):
    global node
    global neigh
    global neigh_rssi
    global target_neigh
    global target_neigh_rssi
    global TOPIC
    global MSG

    neigh = None
    target_neigh = None
    target_neigh_rssi = None
    if pkt.haslayer(Dot11):
        if str(pkt.addr2) != MAC_LIST[int(NODE_ID)-1] and str(pkt.addr1) == "ff:ff:ff:ff:ff:ff" and hasattr(pkt, 'dBm_AntSignal'):
            target_neigh = pkt.addr2
            target_neigh_rssi = pkt.dBm_AntSignal
            if pkt.addr2:
                neigh = get_neighbor()
                try:
                    TOPIC = MAC_LIST[int(NODE_ID) - 1]
                    client.connect(MQTT_SERVER, 1883, 1)
                    #client.loop_forever()
                    #client.loop_stop()
                    neigh = MSG
                    topic = TOPIC
                    print(topic)
                    if target_neigh != neigh:
                        topic = MAC_LIST[int(NODE_ID)-1] + '-target-v2v'
                        msg = '{},{}'.format(target_neigh, target_neigh_rssi)
                    else:
                        msg = '{},{}'.format(neigh, target_neigh_rssi)
                    print("Sending %s to %s" % (msg, topic))
                    mosquitto_publish(topic, msg)
                except:
                    pass


def on_connect(client, userdata, flags, rc):
    global TOPIC
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    global MSG
    MSG = msg.payload.decode().split(',')[0]
    client.disconnect()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


if __name__ == '__main__':
    while True:
        sniff(iface="car%s-mon1" % NODE_ID,
              lfilter=lambda x: x.haslayer(Dot11), prn=pkt_callback_adhoc, store=0, count=11)
        sleep(2)

