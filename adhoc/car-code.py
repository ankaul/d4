import logging
import subprocess
import sys
import os
import re
from time import sleep

logging.basicConfig(level="INFO")

_macMatchRegex = re.compile( r'..:..:..:..:..:..' )
NODE_ID = int(sys.argv[1])
GW = int(sys.argv[2])

CLIENT = '02:00:00:00:00:%02d' % NODE_ID
MININET_WIFI_DIR = '~/mininet-wifi/util/m'
MAC_LIST = ['02:00:00:00:01:00', '02:00:00:00:03:00',
            '02:00:00:00:05:00', '02:00:00:00:07:00',
            '02:00:00:00:09:00', '02:00:00:00:0b:00',
            '02:00:00:00:0d:00', '02:00:00:00:0f:00',
            '02:00:00:00:11:00', '02:00:00:00:13:00']
ADHOC_ROUTE = []
print("Using IEEE 802.11p")


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
    try:
        del_infra_ip()
    except:
        pass


def get_neigh():
    cmd = ["%s car%s batctl bat0 n | awk {'print $2'}" % (MININET_WIFI_DIR, NODE_ID)]
    address = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    link = str(out).split('\n')[2] # it works with 0 for me
    macs = _macMatchRegex.findall(link)
    valid_mac = []
    for mac in macs:
        if mac > MAC_LIST[NODE_ID-1]:
            valid_mac.append(mac)
    if valid_mac:
        return min(valid_mac)
    return None


def get_link():
    cmd = ["%s car%s iw dev car%s-wlan0 link" % (MININET_WIFI_DIR, NODE_ID, NODE_ID)]
    address = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    link = str(out).split('\n')[2]  # it works with 0 for me
    return link


def check_iw_connection():
    sleep(1)
    global GW
    global NODE_ID
    if "Not connected" in str(get_link()):
        if NODE_ID == 1:
            neigh = get_neigh()
            if neigh:
                set_route_v2v('192.168.123.%s' % GW)
                sys.exit()
        else:
            neigh = get_neigh()
            if neigh:
                if ('192.168.123.%s' % (MAC_LIST.index(neigh)+1)) not in ADHOC_ROUTE:
                    set_route_v2v('192.168.123.%s' % GW)
                    ADHOC_ROUTE.append('192.168.123.%s' % (MAC_LIST.index(neigh)+1))
                    sys.exit()


while True:
    check_iw_connection()
