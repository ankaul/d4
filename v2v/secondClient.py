import sys
import os

SUMO_HOME = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "/usr/share/sumo")
sys.path.append(os.path.join(os.environ.get("SUMO_HOME", SUMO_HOME), "tools"))

import traci   # must be placed after the SUMO stuff above

MININET_WIFI_DIR = '~/mininet-wifi/util/m'
NODE_ID = int(sys.argv[1])
SCENARIO = str(sys.argv[2])

PORT = 8813
ADDR = '172.210.0.1'
traci.init(PORT, 10, ADDR)  # port, numRetries, host
traci.setOrder(2)  # number can be anything as long as each client gets its own number

PING_STARTED = False
TC_SET = False
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    if int(traci.simulation.getTime()) == 10 and not PING_STARTED:
        os.system('%s car%s ping 192.168.254.100 > ping.txt &' % (MININET_WIFI_DIR, NODE_ID))
        PING_STARTED = True
    elif int(traci.simulation.getTime()) == 260:
        os.system("pkill -9 -f \'ping\'")
        exit()
