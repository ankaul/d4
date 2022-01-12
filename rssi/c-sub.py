import logging
import socket
import sys
import os
import re
from paho.mqtt.client import Client
from subprocess import check_output as co
import datetime

logging.basicConfig(level="INFO")

BSSID_LIST = ['00:00:00:00:00:01', '00:00:00:00:00:02', '00:00:00:00:00:03']
NODE_ID = int(sys.argv[1])
SCENARIO = sys.argv[2]
CLIENT = '02:00:00:00:00:%02d' % NODE_ID
MININET_WIFI_DIR = '~/mininet-wifi/util/m'
MAC_LIST = ['02:00:00:00:00:00', '02:00:00:00:02:00',
            '02:00:00:00:04:00', '02:00:00:00:06:00',
            '02:00:00:00:08:00', '02:00:00:00:0a:00',
            '02:00:00:00:0c:00', '02:00:00:00:0e:00',
            '02:00:00:00:10:00', '02:00:00:00:12:00']

MAC_LIST_TARGET = ['02:00:00:00:00:00-target', '02:00:00:00:02:00-target',
                   '02:00:00:00:04:00-target', '02:00:00:00:06:00-target',
                   '02:00:00:00:08:00-target', '02:00:00:00:0a:00-target',
                   '02:00:00:00:0c:00-target', '02:00:00:00:0e:00-target',
                   '02:00:00:00:10:00-target', '02:00:00:00:12:00-target']

host_ip = '172.210.0.1'
MQTT_SERVER = '192.168.0.1'
_macMatchRegex = re.compile( r'..:..:..:..:..:..' )
TOPIC = ''
MSG = ''


def mosquitto_subscribe(topic):
    cmd = 'mosquitto_sub -h {} -t {} -C 1'.format(MQTT_SERVER, topic)
    return co(cmd, shell=True)


def mosquitto_publish(topic, bssid):
    cmd = 'mosquitto_pub -h {} -t {} -m {} -r -q 0'.format(MQTT_SERVER, topic, bssid)
    os.system(cmd)


def get_msg(topic):
    global TOPIC
    global MSG

    TOPIC = topic
    client1.connect(MQTT_SERVER, 1883, 1)
    client1.loop_forever()
    client1.loop_stop()
    return MSG


def process_rssi_scenario(msg):
    global TOPIC
    global MSG

    payload = msg.payload.decode('utf-8').split(',')
    infra_mac = MAC_LIST[MAC_LIST_TARGET.index(msg.topic)]
    msg = get_msg(infra_mac).split(',')

    bssid = msg[0]
    rssi = int(msg[1])
    t_bssid = payload[0]
    t_rssi = int(payload[1])
    if bssid != t_bssid:
        if int(bssid[-1]) == NODE_ID:
            if rssi < (t_rssi-2) and t_rssi >= -85:
                msg1 = '{}'.format(infra_mac)
                topic = msg1 + '-handover'
                msg = get_msg(msg1).split(",")[0]
                if msg != t_bssid:
                    now = datetime.datetime.now()
                    logging.info("[{}:{}:{}] Publishing {} to {}...".format(now.hour, now.minute,
                                                                            now.second, t_bssid, topic))
                    client.publish(topic, payload=t_bssid, qos=0, retain=True)
        elif int(bssid) == 0 and t_bssid == BSSID_LIST[NODE_ID - 1] and t_rssi >= -88:
            msg1 = '{}'.format(infra_mac)
            topic = msg1 + '-handover'
            bssid = BSSID_LIST[NODE_ID - 1]
            now = datetime.datetime.now()
            logging.info("[{}:{}:{}] Publishing {} to {}...".format(now.hour, now.minute,
                                                                    now.second, bssid, topic))
            client.publish(topic, payload=bssid, qos=0, retain=True)


def on_connect1(client, userdata, flags, rc):
    global TOPIC
    client1.subscribe(TOPIC)


def on_message1(client, userdata, msg):
    global MSG
    MSG = msg.payload.decode('utf-8')
    client1.disconnect()


def on_connect(client, userdata, flags, rc):
    if SCENARIO == 'distributed':
        topic_list = ['02:00:00:00:00:00-target']
    for topic in topic_list:
        client.subscribe(topic)


def on_message(client, userdata, msg):
    #logging.info("Received " + msg.payload.decode('utf-8'))
    if SCENARIO == 'distributed':
        process_rssi_scenario(msg)


client = Client()
client.on_connect = on_connect
client.on_message = on_message

client1 = Client()
client1.on_connect = on_connect1
client1.on_message = on_message1


while True:
    try:
        client.connect(MQTT_SERVER, 1883, 60)
        logging.info("Connected")
        break
    except:
        pass
client.loop_forever()
