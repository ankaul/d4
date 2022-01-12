import logging
import sys
import os
from paho.mqtt.client import Client

logging.basicConfig(level="INFO")

MAC_LIST = ['02:00:00:00:00:00', '02:00:00:00:02:00',
            '02:00:00:00:04:00', '02:00:00:00:06:00',
            '02:00:00:00:08:00']
AP_MAC_LIST = ['00:00:00:00:00:01', '00:00:00:00:00:02', '00:00:00:00:00:03']
NODE_ID = int(sys.argv[1])
MQTT_SERVER = '192.168.0.1'
NODE_NAME = 'enb%s' % NODE_ID
CLIENT = '02:00:00:00:00:%02d' % NODE_ID
MININET_WIFI_DIR = '~/mininet-wifi/util/m'


def mosquitto_publish(topic, bssid):
    cmd = '{} {} mosquitto_pub -h {} -t {} -m {} -r'.format(
        MININET_WIFI_DIR, NODE_NAME, MQTT_SERVER, topic, bssid)
    os.system(cmd)


def deauth(mac):
    print("Deauthenticating {}".format(mac))
    cmd = "{} {} hostapd_cli -i enb{}-wlan1 deauthenticate {}".format(
        MININET_WIFI_DIR, NODE_NAME, NODE_ID, mac)
    os.system(cmd)


def process_msg(mac):
    deauth(mac)


def on_connect(client, userdata, flags, rc):
    topic_list = ['00:00:00:00:00:01-deauth', '00:00:00:00:00:02-deauth',
                  '00:00:00:00:00:03-deauth']
    for topic in topic_list:
        client.subscribe(topic)


def on_message(client, userdata, msg):
    logging.info("Received " + msg.payload.decode())
    if msg.payload.decode('utf-8') != '0':
        NODE_MAC = AP_MAC_LIST[int(NODE_ID) - 1]
        topic = NODE_MAC + '-deauth'
        mac = msg.payload.decode('utf-8')
        if topic == msg.topic:
            process_msg(mac)
            print("Publishing 0 to {}...".format(topic))
            client.publish(topic, payload='0', qos=2, retain=True)


client = Client()
client.on_connect = on_connect
client.on_message = on_message
while True:
    try:
        client.connect(MQTT_SERVER)
        logging.info("Connected")
        break
    except:
        pass
client.loop_forever()
