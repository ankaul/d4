import logging
import socket
import sys
import os
from paho.mqtt.client import Client
from subprocess import check_output as co
import subprocess
from datetime import datetime

logging.basicConfig(level="INFO")

NODE_ID = int(sys.argv[1])
SCENARIO = sys.argv[2]
SOCKET = sys.argv[3]
SERVER = sys.argv[4]
DELAYED = sys.argv[5]
MSG_SENT = False
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
TOPIC = ''
MSG = ''
MQTT_SERVER = '192.168.254.200'


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
    msg = "car%s.wpa_cli.-i.car%s-wlan0.roam.%s" % (NODE_ID, NODE_ID, bssid)
    s.send(str(msg).encode('utf-8'))
    data = s.recv(1024).decode('utf-8')
    logging.info('Received from server: ' + data)
    s.close()


def process_msg(topic, bssid):
    if 'handover' in topic and bssid != '0':
        handover_message(bssid)


def on_connect(client, userdata, flags, rc):
    topic_list = [MAC_LIST_HANDOVER[NODE_ID-1], MAC_LIST_ADHOC_HANDOVER[NODE_ID-1]]
    if 'distributed' in SCENARIO:
        topic_list.append('02:00:00:00:00:00-set-route')

    for topic in topic_list:
        client.subscribe(topic)


def cur_gateway():
    cmd = ["%s car%s route -n | awk '{print $2}'" % (MININET_WIFI_DIR, NODE_ID)]
    address = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    dest = str(out).split('\n')
    return dest


def add_route(gw):
    os.system("%s car%s route add default gw %s" % (MININET_WIFI_DIR, NODE_ID, gw))


def del_route(gw):
    os.system("%s car%s route del default gw %s" % (MININET_WIFI_DIR, NODE_ID, gw))


def del_infra_ip():
    os.system("%s car%s ifconfig car%s-wlan0 0" % (MININET_WIFI_DIR, NODE_ID, NODE_ID))


def add_infra_ip():
    os.system("%s car%s ifconfig car%s-wlan0 192.168.254.%s" %
              (MININET_WIFI_DIR, NODE_ID, NODE_ID, NODE_ID))


def add_arp_entry():
    os.system("%s car%s arp -s 192.168.254.100 %s" % (MININET_WIFI_DIR, NODE_ID, SERVER))
    os.system("%s car%s arp -s 192.168.254.200 %s" % (MININET_WIFI_DIR, NODE_ID, SOCKET))


def set_route_infra():
    add_infra_ip()
    add_arp_entry()
    del_all_default_gw()


def del_all_default_gw():
    os.system('ip route flush 0/0')


def set_route_v2v(gw):
    del_all_default_gw()
    add_route(gw)
    try:
        del_infra_ip()
    except:
        pass


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
            now = datetime.now()
            client.publish(msg.topic, payload=None, qos=0, retain=True)
            logging.info("[%s:%s:%s] Sending %s,-50 to %s..." % (now.hour, now.minute, now.second,
                                                                 neigh_mac, MAC_LIST_ADHOC[NODE_ID-1]))
            msg1 = '{},{}'.format(neigh_mac, -50)
            mosquitto_publish(MAC_LIST_ADHOC[NODE_ID-1], msg1)
            adhoc_id = MAC_LIST_ADHOC.index(neigh_mac) + 1
            gw = '192.168.123.{}'.format(adhoc_id)
            set_route_v2v(gw)


def process_emergency_msg(msg):
    global MSG_SENT
    emergency_msg = 'setRouteID'
    routeID = msg.payload.decode('utf-8')
    if routeID != '0':
        mac = MAC_LIST[NODE_ID - 1]
        topic = '{}-set-route'.format(mac)
        logging.info("Publishing {} to {}...".format(0, topic))
        mosquitto_publish(topic, '0')
        port = 12345  # Make sure it's within the > 1024 $$ <65535 range
        s = socket.socket()
        s.connect((host_ip, port))
        if int(float(DELAYED)) != 1000 and (NODE_ID == 2 or NODE_ID == 3):
            routeID = 'route4'
        msg = "set.car%s.sumo.%s.%s" % (NODE_ID, emergency_msg, routeID)
        msgTime = 'Vehicle %s: message was received when T=%s' % (NODE_ID, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

        if not MSG_SENT:
            if int(float(DELAYED)) != 1000:
                os.system('echo \"%s\" >> %s' % (msgTime, 'timestamp-%s-delayed.txt' % SCENARIO))
            else:
                os.system('echo \"%s\" >> %s' % (msgTime, 'timestamp-%s.txt' % SCENARIO))
            MSG_SENT = True

        s.send(str(msg).encode('utf-8'))
        data = s.recv(1024).decode('utf-8')
        logging.info('Received from server: ' + data)
        s.close()


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
        elif 'handover' in msg.topic:
            bssid = msg.payload.decode('utf-8')
            if bssid != '0':
                mac = MAC_LIST[NODE_ID - 1]
                bssid_ = get_msg(mac).split(',')

                now = datetime.now()
                topic = bssid_[0] + '-deauth'
                logging.info("[{}:{}:{}] Publishing {} to {}...".format(now.hour, now.minute,
                                                                        now.second, mac, topic))
                client.publish(topic, payload=mac, qos=0, retain=True)
                topic = mac + '-handover'
                logging.info("[{}:{}:{}] Publishing None to {}...".format(now.hour, now.minute,
                                                                          now.second, topic))
                client.publish(topic, payload=None, qos=0, retain=True)
                process_msg(msg.topic, bssid)
                set_route_infra()
        elif 'set-route' in msg.topic:
            process_emergency_msg(msg)


client1 = Client()
client1.on_connect = on_connect1
client1.on_message = on_message1


client = Client()
client.on_connect = on_connect
client.on_message = on_message

while True:
    try:
        client.connect(MQTT_SERVER, 1883, keepalive=1)
        logging.info("Connected")
        break
    except:
        pass
client.loop_forever()
