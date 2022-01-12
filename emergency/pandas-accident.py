#!/usr/bin/env python

import pandas as pd

import subprocess
import matplotlib.pyplot as plt
from itertools import cycle, islice


dist = 'arrival-position-distributed.txt'
cent = 'arrival-position-centralized.txt'
no_ac = 'arrival-position-no_accident.txt'

del_dist = 'arrival-position-delayed-distributed.txt'
del_cent = 'arrival-position-delayed-centralized.txt'

td = []
tc = []
no = []
delay_td = []
delay_tc = []

for car_id in range(0, 10):
    get_t = 'cat %s-%s' % (car_id, dist)
    address = subprocess.Popen(get_t, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    td.append(float(out.decode().split('\n')[0]))

for car_id in range(0, 10):
    get_t = 'cat %s-%s' % (car_id, del_dist)
    address = subprocess.Popen(get_t, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    delay_td.append(float(out.decode().split('\n')[0]))

for car_id in range(0, 10):
    get_t = 'cat %s-%s' % (car_id, cent)
    address = subprocess.Popen(get_t, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    tc.append(float(out.decode().split('\n')[0]))

for car_id in range(0, 10):
    get_t = 'cat %s-%s' % (car_id, no_ac)
    address = subprocess.Popen(get_t, stdout=subprocess.PIPE, shell=True)
    (out, err) = address.communicate()
    no.append(float(out.decode().split('\n')[0]))

fig, ax1 = plt.subplots()
fig_name = "accident-results.eps"
ax = plt.gca()

index = ['veh1', 'veh2', 'veh3', 'veh4', 'veh5', 'veh6', 'veh7', 'veh8', 'veh9', 'veh10']

df = pd.DataFrame({'No-accident scenario': no, 'Delayed message': delay_td, 'Distributed Control': td, 'Centralized Control': tc}, index=index)
colors = list(islice(cycle(['chartreuse', 'gold', 'dodgerblue', 'orangered']), None, len(df)))
ax = df.plot.bar(color=colors, rot=0)

ax.set_xlabel("Vehicles", fontsize=15)
ax.set_ylabel("Time (s)", fontsize=15)

max_y = max(delay_td) + 170
ax.set_ylim([0, max_y])

plt.savefig(fig_name)
