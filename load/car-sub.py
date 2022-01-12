import logging
import socket
import sys
import os
import re
from paho.mqtt.client import Client
from subprocess import check_output as co
import datetime

logging.basicConfig(level="INFO")

_macMatchRegex = re.compile( r'..:..:..:..:..:..' )
NODE_ID = int(sys.argv[1])
SCENARIO = sys.argv[2]
CLIENT = '02:00:00:00:00:%02d' % NODE_ID
MININET_WIFI_DIR = '~/mininet-wifi/util/m'
MAC_LIST = ['02:00:00:00:00:00', '02:00:00:00:02:00',
            '02:00:00:00:04:00', '02:00:00:00:06:00',
            '02:00:00:00:08:00', '02:00:00:00:0a:00',
            '02:00:00:00:0c:00', '02:00:00:00:0e:00',
            '02:00:00:00:10:00', '02:00:00:00:12:00']
MAC_LIST_HANDOVER = ['02:00:00:00:00:00-handover', '02:00:00:00:02:00-handover',
            '02:00:00:00:04:00-handover', '02:00:00:00:06:00-handover',
            '02:00:00:00:08:00-handover', '02:00:00:00:0a:00-handover',
            '02:00:00:00:0c:00-handover', '02:00:00:00:0e:00-handover',
            '02:00:00:00:10:00-handover', '02:00:00:00:12:00-handover']
host_ip = '172.210.0.1'
MQTT_SERVER = '192.168.254.200'
TOPIC = ''
MSG = ''


def mosquitto_subscribe(topic):
    return co('mosquitto_sub -h %s -t \"%s\" -C 1' % (MQTT_SERVER, topic), shell=True)


def mosquitto_publish(topic, bssid):
    cmd = 'mosquitto_pub -h {} -t {} -m {} -r -q 0'.format(MQTT_SERVER, topic, bssid)
    os.system(cmd)


def handover_message(bssid):
    logging.info("Handovering to %s" % bssid)
    host = host_ip
    port = 12345  # Make sure it's within the > 1024 $$ <65535 range
    s = socket.socket()
    s.connect((host, port))
    msg = "set.car%s.roam(%s, intf=car%s-wlan0)" % (NODE_ID, bssid, NODE_ID)
    s.send(str(msg).encode('utf-8'))
    data = s.recv(1024).decode('utf-8')
    logging.info('Received from server: ' + data)
    s.close()


def process_msg(topic, bssid):
    if 'handover' in topic and bssid != '0':
        handover_message(bssid)
        topic = MAC_LIST[NODE_ID - 1]
        client.publish(topic, payload=bssid, qos=0, retain=True)


def on_connect(client, userdata, flags, rc):
    topic_list = ['02:00:00:00:00:00-handover']
    for topic in topic_list:
        client.subscribe(topic)


def get_msg(topic):
    global TOPIC
    global MSG

    TOPIC = topic
    client1.connect(MQTT_SERVER, 1883, 1)
    client1.loop_forever()
    client1.loop_stop()
    return MSG


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
        if 'handover' in msg.topic:
            t_bssid = msg.payload.decode('utf-8')
            bssid = _macMatchRegex.findall(msg.topic)[0]
            if t_bssid != '0' and t_bssid != bssid:
                mac = MAC_LIST[NODE_ID - 1]
                bssid_ = get_msg(mac).split(',')

                now = datetime.datetime.now()
                topic = bssid_[0] + '-deauth'
                logging.info("[{}:{}:{}] Publishing {} to {}...".format(now.hour, now.minute,
                                                                        now.second, mac, topic))
                client.publish(topic, payload=mac, qos=0, retain=True)
                topic = mac + '-handover'
                logging.info("[{}:{}:{}] Publishing None to {}...".format(now.hour, now.minute,
                                                                          now.second, topic))
                client.publish(topic, payload='0', qos=0, retain=True)
                process_msg(msg.topic, t_bssid)


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
