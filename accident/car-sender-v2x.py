#!/usr/bin/python

from scapy.all import *
import sys
import os
import subprocess
from subprocess import check_output as co
from time import sleep
import paho.mqtt.client as mqtt


NODE_ID = int(sys.argv[1])
SCENARIO = str(sys.argv[2])

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


def get_candidate_neighbors():
    cmd = ["%s car%s batctl meshif bat0 n | awk '{print $2}'" % (MININET_WIFI_DIR, NODE_ID)]
    address = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    gw = str(out).split('\n')
    gw.sort()
    return gw[1]


def get_neighbor():
    cmd = ["%s car%s route -n | awk '{print $2}'" % (MININET_WIFI_DIR, NODE_ID)]
    address = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    dest = str(out).split('\n')
    return dest


def get_link():
    cmd = ["%s car%s iw dev car%s-wlan0 link" % (MININET_WIFI_DIR, NODE_ID, NODE_ID)]
    address = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    link = str(out).split('\n')[0]
    return link


def get_nghb_ip(gw):
    nghb_id = MAC_LIST.index(gw) + 1
    nghb_ip = '192.168.123.%s' % nghb_id
    return nghb_ip


def get_bssid():
    cmd = ["%s car%s wpa_cli -i car%s-wlan0 status" % (MININET_WIFI_DIR, NODE_ID, NODE_ID)]
    address = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    if 'SCAN' not in str(out).split('\n')[0]:
        return str(out).split('\n')[0][6:]
    return None


def mosquitto_publish(topic, bssid):
    cmd = 'mosquitto_pub -h {} -t {} -m {} -r'.format(MQTT_SERVER, topic, bssid)
    os.system(cmd)


def mosquitto_subscribe(topic):
    cmd = 'mosquitto_sub -h {} -t {} -C 1'.format(MQTT_SERVER ,topic)
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
        if str(pkt.addr2) != MAC_LIST[int(NODE_ID)-1] and str(pkt.addr1) == "ff:ff:ff:ff:ff:ff":
            target_neigh = pkt.addr2
            target_neigh_rssi = pkt.dBm_AntSignal
            if pkt.addr2:
                neigh = get_neighbor()
                try:
                    TOPIC = MAC_LIST[int(NODE_ID) - 1]
                    client.connect(MQTT_SERVER, 1883, 1)
                    client.loop_forever()
                    client.loop_stop()
                    neigh = MSG
                    topic = TOPIC
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
    MSG = str(msg.payload).split(',')[0]
    client.disconnect()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


if __name__ == '__main__':
    while True:
        sniff(iface="car%s-mon1" % NODE_ID,
              lfilter=lambda x: x.haslayer(Dot11), prn=pkt_callback_adhoc, store=0, count=11)
        sleep(2)

