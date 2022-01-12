import logging
import sys
import re
from paho.mqtt.client import Client
import datetime

logging.basicConfig(level="INFO")

NODE_ID = int(sys.argv[1])
SCENARIO = sys.argv[2]
CLIENT = '02:00:00:00:00:%02d' % NODE_ID
MININET_WIFI_DIR = '~/mininet-wifi/util/m'
MAC_LIST = ['02:00:00:00:00:00', '02:00:00:00:02:00',
            '02:00:00:00:04:00', '02:00:00:00:06:00',
            '02:00:00:00:08:00', '02:00:00:00:0a:00',
            '02:00:00:00:0c:00', '02:00:00:00:0e:00',
            '02:00:00:00:10:00', '02:00:00:00:12:00']

MAC_LIST_ADHOC_HANDOVER = ['02:00:00:00:01:00-handover-v2v', '02:00:00:00:03:00-handover-v2v',
                           '02:00:00:00:05:00-handover-v2v', '02:00:00:00:07:00-handover-v2v',
                           '02:00:00:00:09:00-handover-v2v', '02:00:00:00:0b:00-handover-v2v',
                           '02:00:00:00:0d:00-handover-v2v', '02:00:00:00:0f:00-handover-v2v',
                           '02:00:00:00:11:00-handover-v2v', '02:00:00:00:13:00-handover-v2v']


MAC_LIST_ADHOC = ['02:00:00:00:01:00', '02:00:00:00:03:00',
                  '02:00:00:00:05:00', '02:00:00:00:07:00',
                  '02:00:00:00:09:00', '02:00:00:00:0b:00',
                  '02:00:00:00:0d:00', '02:00:00:00:0f:00',
                  '02:00:00:00:11:00', '02:00:00:00:13:00']

MAC_LIST_ADHOC_TARGET = ['02:00:00:00:01:00-target-v2v', '02:00:00:00:03:00-target-v2v',
                         '02:00:00:00:05:00-target-v2v', '02:00:00:00:07:00-target-v2v',
                         '02:00:00:00:09:00-target-v2v', '02:00:00:00:0b:00-target-v2v',
                         '02:00:00:00:0d:00-target-v2v', '02:00:00:00:0f:00-target-v2v',
                         '02:00:00:00:11:00-target-v2v', '02:00:00:00:13:00-target-v2v']

host_ip = '172.210.0.1'
MQTT_SERVER = '192.168.0.1'
_macMatchRegex = re.compile( r'..:..:..:..:..:..' )
TOPIC = ''
MSG = ''


def get_msg(topic):
    global TOPIC
    global MSG

    TOPIC = topic
    client1.connect(MQTT_SERVER, 1883, 1)
    client1.loop_forever()
    client1.loop_stop()
    return MSG


def pub_v2v(topic, t_neigh, infra):
    msg = '{}'.format(t_neigh)
    now = datetime.datetime.now()
    logging.info("[{}:{}:{}] Publishing {} to {}...".format(now.hour, now.minute,
                                                            now.second, msg, topic))
    client.publish(topic, payload=msg, qos=0, retain=True)


def process_v2v_scenario(msg):
    if msg.topic in MAC_LIST_ADHOC_TARGET:
        t_neigh = msg.payload.decode('utf-8').split(',')[0]
        index = MAC_LIST_ADHOC_TARGET.index(msg.topic)

        adhoc_mac = MAC_LIST_ADHOC[index]
        infra_mac = MAC_LIST[index]

        neigh = get_msg(adhoc_mac).split(',')
        neigh = neigh[0]

        adhoc_mac += '-handover-v2v'
        # if veh is associated with BS
        infra = get_msg(infra_mac).split(',')
        if int(infra[1]) < -87:  # and int(t_infra[1]) >= -85:
            if neigh == '0':
                t_neigh = MAC_LIST_ADHOC[MAC_LIST_ADHOC_HANDOVER.index(adhoc_mac)+1]
                pub_v2v(adhoc_mac, t_neigh, infra)
            else:
                # two vehs cannot have opposite veh as neigh
                itself = get_msg(t_neigh).split(',')[0]
                if MAC_LIST_ADHOC[NODE_ID - 1] != itself:
                    pub_v2v(adhoc_mac, t_neigh, infra)


def on_connect1(client, userdata, flags, rc):
    global TOPIC
    client1.subscribe(TOPIC)


def on_message1(client, userdata, msg):
    global MSG
    MSG = msg.payload.decode('utf-8')
    client1.disconnect()


def on_connect(client, userdata, flags, rc):
    topic_list = MAC_LIST_ADHOC_TARGET + ['02:00:00:00:00:00-target']
    for topic in topic_list:
        client.subscribe(topic)


def on_message(client, userdata, msg):
    process_v2v_scenario(msg)


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
