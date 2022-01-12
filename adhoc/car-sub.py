import logging
import sys
import os
import re
from paho.mqtt.client import Client
import datetime

logging.basicConfig(level="INFO")

_macMatchRegex = re.compile( r'..:..:..:..:..:..' )
NODE_ID = int(sys.argv[1])
SOCKET = sys.argv[2]
SERVER = sys.argv[3]

CLIENT = '02:00:00:00:00:%02d' % NODE_ID
MININET_WIFI_DIR = '~/mininet-wifi/util/m'

MAC_LIST_HANDOVER = ['02:00:00:00:00:00-handover', '02:00:00:00:02:00-handover',
            '02:00:00:00:04:00-handover', '02:00:00:00:06:00-handover',
            '02:00:00:00:08:00-handover', '02:00:00:00:0a:00-handover',
            '02:00:00:00:0c:00-handover', '02:00:00:00:0e:00-handover',
            '02:00:00:00:10:00-handover', '02:00:00:00:12:00-handover']
MAC_LIST_ADHOC = ['02:00:00:00:01:00', '02:00:00:00:03:00',
                  '02:00:00:00:05:00', '02:00:00:00:07:00',
                  '02:00:00:00:09:00', '02:00:00:00:0b:00',
                  '02:00:00:00:0d:00', '02:00:00:00:0f:00',
                  '02:00:00:00:11:00', '02:00:00:00:13:00']
MAC_LIST_ADHOC_HANDOVER = ['02:00:00:00:01:00-handover-v2v', '02:00:00:00:03:00-handover-v2v',
                           '02:00:00:00:05:00-handover-v2v', '02:00:00:00:07:00-handover-v2v',
                           '02:00:00:00:09:00-handover-v2v', '02:00:00:00:0b:00-handover-v2v',
                           '02:00:00:00:0d:00-handover-v2v', '02:00:00:00:0f:00-handover-v2v',
                           '02:00:00:00:11:00-handover-v2v', '02:00:00:00:13:00-handover-v2v']

host_ip = '172.210.0.1'
MQTT_SERVER = '192.168.254.200'
TOPIC = ''
MSG = ''


def mosquitto_publish(topic, bssid):
    cmd = 'mosquitto_pub -h {} -t {} -m {} -r -q 0'.format(MQTT_SERVER, topic, bssid)
    os.system(cmd)


def on_connect(client, userdata, flags, rc):
    topic_list = [MAC_LIST_HANDOVER[NODE_ID-1], MAC_LIST_ADHOC_HANDOVER[NODE_ID-1]]
    for topic in topic_list:
        client.subscribe(topic)


def add_route(gw):
    os.system("%s car%s route add default gw %s" % (MININET_WIFI_DIR, NODE_ID, gw))


def del_route(gw):
    os.system("%s car%s route del default gw %s" % (MININET_WIFI_DIR, NODE_ID, gw))


def del_infra_ip():
    os.system("%s car%s ifconfig car%s-wlan0 0" % (MININET_WIFI_DIR, NODE_ID, NODE_ID))


def del_all_default_gw():
    os.system('ip route flush 0/0')


def set_route_v2v(gw):
    del_all_default_gw()
    add_route(gw)
    del_infra_ip()


def get_msg(topic):
    global TOPIC
    global MSG

    TOPIC = topic
    client1.connect(MQTT_SERVER, 1883, 1)
    client1.loop_forever()
    client1.loop_stop()
    return MSG


def process_v2v_msg(msg):
    neigh_mac = msg.payload.decode('utf-8')
    adhoc_mac = MAC_LIST_ADHOC[MAC_LIST_ADHOC_HANDOVER.index(msg.topic)]
    if neigh_mac != '0' and adhoc_mac == MAC_LIST_ADHOC[NODE_ID-1]:
        if neigh_mac in MAC_LIST_ADHOC:
            now = datetime.datetime.now()
            client.publish(msg.topic, payload=None, qos=0, retain=True)
            logging.info("[%s:%s:%s] Sending %s,-50 to %s..." % (now.hour, now.minute, now.second,
                                                                 neigh_mac, MAC_LIST_ADHOC[NODE_ID-1]))
            msg1 = '{},{}'.format(neigh_mac, -50)
            mosquitto_publish(MAC_LIST_ADHOC[NODE_ID - 1], msg1)
            gw = '192.168.123.{}'.format(NODE_ID + 1)
            set_route_v2v(gw)
            sys.exit()


def on_connect1(client, userdata, flags, rc):
    global TOPIC
    client1.subscribe(TOPIC)


def on_message1(client, userdata, msg):
    global MSG
    MSG = msg.payload.decode('utf-8')
    client1.disconnect()


def on_message(client, userdata, msg):
    logging.info("Received " + msg.payload.decode('utf-8'))
    if msg.payload.decode('utf-8'):
        global TOPIC
        global MSG
        if 'handover-v2v' in msg.topic:
            process_v2v_msg(msg)


client1 = Client()
client1.on_connect = on_connect1
client1.on_message = on_message1


client = Client()
client.on_connect = on_connect
client.on_message = on_message

while True:
    try:
        client.connect(MQTT_SERVER, 1883, keepalive=2)
        logging.info("Connected")
        break
    except:
        pass
client.loop_forever()
