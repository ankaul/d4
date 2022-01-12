import sys
import os
import glob
from datetime import datetime
SUMO_HOME = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "/usr/share/sumo")
sys.path.append(os.path.join(os.environ.get("SUMO_HOME", SUMO_HOME), "tools"))
import traci
import os.path

PORT = 8813
ADDR = '172.210.0.1'
traci.init(PORT, 10, ADDR)  # port, numRetries, host
traci.setOrder(2)  # number can be anything as long as each client gets its own number

vehID = sys.argv[1]
SCENARIO = sys.argv[2]
DELAYED = sys.argv[3]

for n in range(0, 10):
    if int(float(DELAYED)) != 1000:
        file = '{}-arrival-position-delayed-{}.txt'.format(n, SCENARIO)
    else:
        file = '{}-arrival-position-{}.txt'.format(n, SCENARIO)
    if glob.glob(file):
        os.system('rm %s' % file)

ACCIDENT_SET = False
RESUME_SET = False
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    if 'no_accident' not in SCENARIO:
        if float(traci.simulation.getTime()) > 82.6 and not ACCIDENT_SET:
        #if int(traci.simulation.getTime()) > 126 and not ACCIDENT_SET:
            traci.vehicle.setSpeed('0', 0)
            os.system('python simulate_accident.py %s %s %s &' % (vehID, SCENARIO, DELAYED))
            ACCIDENT_SET = True
            print('Attention! car1 was involved in an accident!')
            msgTime = 'Sumo: message was sent when T=%s' % datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            if int(float(DELAYED)) != 1000:
                os.system('echo \"%s\" >> %s' % (msgTime, 'timestamp-%s-delayed.txt' % SCENARIO))
            else:
                os.system('echo \"%s\" >> %s' % (msgTime, 'timestamp-%s.txt' % SCENARIO))
        if int(traci.simulation.getTime()) > 265 and not RESUME_SET:
            traci.vehicle.setSpeed('0', 12)
            RESUME_SET = True

    for vehID1 in traci.vehicle.getIDList():
        if 0 <= int(vehID1) < 10:
            x1 = int(traci.vehicle.getPosition(vehID1)[0])
            if int(float(DELAYED)) != 1000:
                file = '{}-arrival-position-delayed-{}.txt'.format(vehID1, SCENARIO)
            else:
                file = '{}-arrival-position-{}.txt'.format(vehID1, SCENARIO)
            if x1 >= 3444 and not os.path.isfile(file):
                os.system('echo \"%s\" > %s' % (traci.simulation.getTime(), file))
