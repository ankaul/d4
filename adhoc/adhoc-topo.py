#!/usr/bin/python

from time import sleep
import os
import sys

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd, adhoc, ITSLink
from mininet.term import makeTerm
from mn_wifi.wmediumdConnector import interference
from mn_wifi.sumo.runner import sumo
from mn_wifi.bmv2 import P4AP, P4Host


def config_br():
    os.system('brctl addbr br0')
    os.system('ip addr add dev br0 172.210.0.1/16')
    os.system('ip link set br0 up')


def topology():

    arg = sys.argv
    SCENARIO = arg[1]
    host_ip = '172.210.0.1'
    host_net = '172.210.0.0/16'
    ip_c0 = '192.168.0.2'
    ip_mosquitto = '192.168.0.1'

    os.system('sudo mn -c')
    os.system('sudo fuser -k 6690/tcp')
    os.system('sudo fuser -k 6691/tcp')
    os.system('sudo fuser -k 6692/tcp')
    os.system('sudo systemctl stop firewalld')

    "Create a network."
    net = Mininet_wifi(listenPort=6640, link=wmediumd,
                       wmediumd_mode=interference, ipBase='192.168.100.0',
                       disable_tcp_checksum=True)

    info("*** Creating nodes\n")
    for id in range(0, 10):
        net.addCar('car%s' % (id+1), wlans=2, encrypt=['wpa2', ''],
                   ip='192.168.254.%s/24' % (id+1),
                   bgscan_threshold=-70, s_inverval=2,
                   l_interval=2, bgscan_module='learn',
                   scan_freq='5180', freq_list='5180')

    enb_pos = ['2200,3600,0', '2600,3150,0', '2900,3000,0']

    # Add APs
    path = os.path.dirname(os.path.abspath(__file__))
    json_file = path + '/ap_runtime.json'
    config1 = path + '/commands_enb1.txt'
    enb1 = net.addAccessPoint('enb1', mac='00:00:00:00:00:01', ssid="handover",
                              mode="a", channel="36", datapath='user',
                              passwd='123456789a', encrypt='wpa2',
                              dpid='1', position=enb_pos[0], inNamespace=True,
                              country_code='DE', netcfg=True, json=json_file, thriftport=50001,
                              switch_config=config1, cls=P4AP)

    # Add hosts
    h0 = net.addHost('h0', ip=ip_mosquitto, cls=P4Host)
    h1 = net.addHost('h1', ip=ip_c0, cls=P4Host)
    wan0 = net.addHost('wan0', ip='192.168.254.100/24', inNamespace=False)

    # nat1 is a switch for "GPS" and socket purposes
    s2 = net.addSwitch('s2', mac='00:00:00:00:00:04', dpid='4', failMode='standalone')
    s3 = net.addSwitch('s3', mac='00:00:00:00:00:05', dpid='5', failMode='standalone')
    s10 = net.addSwitch('s10', mac='00:00:00:00:00:06', dpid='6', failMode='standalone')
    nat1 = net.addSwitch('nat1', mac='00:00:00:00:00:09', dpid='9', failMode='standalone')

    os.system('sudo service network-manager stop')
    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=2.6)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Associating Stations\n")
    net.addLink(s10, enb1)
    net.addLink(s10, h1)
    net.addLink(s2, s10)
    net.addLink(s2, h0)
    net.addLink(s3, enb1, bw=100)
    net.addLink(s3, wan0, bw=100, delay='10ms')

    for car in net.cars:
        net.addLink(nat1, car)  # connecting cars to nat1 for GPS purposes
    for host in net.hosts:
        if host != wan0 and host != h0:
            net.addLink(nat1, host)  # connecting cars to nat1 for GPS purposes

    net.addLink(s3, h0)

    info("*** Configuring MANET routing protocol\n")
    for car in net.cars:
        car.cmd('ifconfig %s-wlan1 172.16.0.%d' % (car.name, net.cars.index(car)+1))

    os.system('sudo iw reg set DE')
    for car in net.cars:
        net.addLink(car, cls=ITSLink, intf='%s-wlan1' % car.name,
                    bandChannel=10, channel='181', ssid='adhocNet', proto='batman_adv')  # flags='-h 1')

    info("*** Starting SUMO\n")
    net.useExternalProgram(program=sumo, port=8813,
                           extra_params=["--start --delay 1000"],
                           config_file='map.sumocfg', clients=2)

    #nodes = net.cars + net.aps
    #net.telemetry(nodes=nodes, data_type='position',
    #              min_x=2000, min_y=2500,
    #              max_x=3500, max_y=4000)

    info("*** Starting network\n")
    net.build()
    os.system('sudo service network-manager start')
    net.addNAT(name='socket0', linkTo='nat1', ip='192.168.100.254',
               net=host_net).configDefault()
    sleep(2)
    enb1.start([])
    nat1.start([])
    s2.start([])
    s3.start([])
    s10.start([])

    #os.system('sudo service network-manager stop')
    config_br()
    info("*** Start Socket Server\n")
    net.socketServer(ip=host_ip, port=12345)

    wan0.cmd('iptables -I FORWARD -i wan0-eth0 -d 192.168.254.0/24 -j DROP')
    wan0.cmd('iptables -I FORWARD -i wan0-eth0 -s 192.168.254.0/24 -j ACCEPT')
    wan0.cmd('iptables -I FORWARD -o wan0-eth0 -d 192.168.254.0/24 -j ACCEPT')
    wan0.cmd('iptables -t nat -A POSTROUTING -s 192.168.254.0/24 \'!\' -d 192.168.0.0/24 -j MASQUERADE')

    sleep(3)

    enb1.cmd('sysctl net.ipv4.ip_forward=1')
    s2.cmd('sysctl net.ipv4.ip_forward=1')

    h0.setIP('192.168.254.200/24', intf='h0-eth1')

    enb1.cmd('ifconfig enb1-eth2 192.168.0.201')

    for car in net.cars:
        car.cmd('iw dev %s-wlan1 interface add %s-mon1 type monitor' % (car.name, car.name))
        car.cmd('ifconfig %s-mon1 up' % car.name)
        car.cmd('ifconfig lo up')

    for idx, car in enumerate(net.cars):
        car.cmd('ifconfig %s-eth2 192.168.100.%s/24' % (car, (int(idx)+1)))
        net.setStaticRoute(node=car, ip='192.168.100.254', net='192.168.0.0/24')

    for car in net.cars:
        for intf in car.wintfs.values():
            car.cmd('iptables -t nat -A POSTROUTING -o %s -j MASQUERADE' % intf.name)
        car.cmd('iptables -t nat -A POSTROUTING -o bat0 -j MASQUERADE')
        car.cmd('ip route add %s via 192.168.100.254' % host_net)
        car.cmd('sysctl net.ipv4.ip_forward=1')

    nodes = [h1]
    for idx, node in enumerate(nodes):
        node.cmd('ifconfig %s-eth2 192.168.100.%s/24' % (node, int(idx)+50))
        node.cmd('ip route add %s via 192.168.100.254' % host_net)

    if SCENARIO == 'no-controller':
        for id in range(1, 11):
            makeTerm(net.cars[id-1], title='check-conn', cmd="bash -c 'python car-code.py %d %s;'" % (id, arg[2]))
    else:
        mqtt_cmd = ''
        for car in net.cars:
            mqtt_cmd += 'mosquitto_sub -h 192.168.0.1 -t \"%s\" -C 1 & ' % car.name
        for controller in net.controllers:
            mqtt_cmd += 'mosquitto_sub -h 192.168.0.1 -t \"%s\" -C 1 & ' % controller.name

        makeTerm(h0, title='mosquitto', cmd="bash -c 'mosquitto;'")
        h1.cmd(mqtt_cmd)

        makeTerm(enb1, title='bs-sender', cmd="bash -c 'python bs-sender.py 1 %s;'" % SCENARIO)

        #if 'distributed' in SCENARIO:
        makeTerm(h1, title='c-sub-pub', cmd="bash -c 'python c-sub.py 1 %s;'" % SCENARIO)

        makeTerm(enb1, title='sub', cmd="bash -c 'python enb-sub.py 1;'")

        sleep(1)
        for car in net.cars:
            h1.cmd('mosquitto_pub -h 192.168.0.1 -t {}-handover -m 0 -r'.format(car.wintfs[0].mac))
            h1.cmd('mosquitto_pub -h 192.168.0.1 -t {} -m \"0,-100\" -r'.format(car.wintfs[0].mac))

            h1.cmd('mosquitto_pub -h 192.168.0.1 -t {}-handover-v2v -m 0 -r'.format(car.wintfs[1].mac))
            h1.cmd('mosquitto_pub -h 192.168.0.1 -t {} -m \"0,-100\" -r'.format(car.wintfs[1].mac))

    makeTerm(net.cars[0], title='sumoClient',
             cmd="bash -c 'python secondClient.py %s %s;'" % (1, SCENARIO))

    if SCENARIO != 'no-controller':
        for id, car in enumerate(net.cars):
            makeTerm(car, title='sender', cmd="bash -c 'python car-sender-v2x.py %d %s;'" % (id+1, SCENARIO))

            SERVER = wan0.intfs[0].mac
            SOCKET = h0.intfs[1].mac
            makeTerm(car, title='car-sub', cmd="bash -c 'python car-sub.py %d %s %s %s;'" % (id+1, SCENARIO, SOCKET, SERVER))
            print("%d %s %s %s;'" % (id, SCENARIO, SOCKET, SERVER))

    #net.staticArp()
    sleep(5)
    for car in net.cars:
        for h in net.hosts:
            for intf in h.intfs.values():
                car.cmd('arp -s %s %s' % (intf.ip, intf.mac))

    for h in net.hosts:
        for car in net.cars:
            for intf in car.intfs.values():
                h.cmd('arp -s %s %s' % (intf.ip, intf.mac))

    sleep(2)
    for ap in net.aps:
        ap.cmd('mosquitto_pub -h 192.168.0.1 -t "%s" -m \"0\" -r' % ap.wintfs[0].mac)

    for car in net.cars:
        car.cmd('route add default gw 192.168.254.100')

    info("*** Running CLI\n")
    CLI(net)

    if SCENARIO == 'no-controller':
        os.system('mv ping.txt ping-%s-%s.txt' % (SCENARIO, arg[2]))
    else:
        os.system('mv ping.txt ping-%s.txt' % SCENARIO)

    os.system('pkill -9 -f \"xterm -title\"')
    os.system('pkill -9 -f \"sumo-gui\"')
    os.system('pkill -9 -f \"bs-sender\"')
    os.system('pkill -9 -f \"test.sh\"')
    os.system('pkill -9 -f \"mosquitto\"')

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
