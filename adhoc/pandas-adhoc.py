#!/usr/bin/env python

from pandas import DataFrame

import subprocess
import math
import matplotlib.pyplot as plt
import numpy as np

file1 = 'ping-no-controller-2.txt'
file2 = 'ping-no-controller-7.txt'
file3 = 'ping-controller.txt'

latency_no_controller = 'grep -r \"ms\" %s | awk \'{print $7}\' | tr -d \"time=\"' % file1
icmp_seq_v2v = 'grep -r \"ms\" %s | awk \'{print $5}\' | tr -d "icmp_seq="' % file1
latency_no_controller_7 = 'grep -r \"ms\" %s | awk \'{print $7}\' | tr -d \"time=\"' % file2
icmp_seq_v2v_7 = 'grep -r \"ms\" %s | awk \'{print $5}\' | tr -d "icmp_seq="' % file2
latency = 'grep -r \"ms\" %s | awk \'{print $7}\' | tr -d \"time=\"' % file3
icmp_seq = 'grep -r \"ms\" %s | awk \'{print $5}\' | tr -d "icmp_seq="' % file3
x_limit = 170

address = subprocess.Popen(latency, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
latency_ = out.decode().split('\n')

address = subprocess.Popen(icmp_seq, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
icmp_seq_ = out.decode().split('\n')

address = subprocess.Popen(latency_no_controller, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
latency_no_controller_ = out.decode().split('\n')

address = subprocess.Popen(icmp_seq_v2v, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
icmp_seq_v2v_ = out.decode().split('\n')

address = subprocess.Popen(latency_no_controller_7, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
latency_no_controller_7_ = out.decode().split('\n')

address = subprocess.Popen(icmp_seq_v2v_7, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
icmp_seq_v2v_7_ = out.decode().split('\n')

latency_no_controller = []
icmp_seq_v2v = []
latency_no_controller_7 = []
icmp_seq_v2v_7 = []
latency = []
icmp_seq = []

id = 0
for n in range(0, x_limit):
    if str(n) in icmp_seq_v2v_:
        icmp_seq_v2v.append(int(icmp_seq_v2v_[id]))
        latency_no_controller.append(float(latency_no_controller_[id]))
        id += 1
    else:
        icmp_seq_v2v.append(float(n))
        latency_no_controller.append(None)

id = 0
for n in range(0, x_limit):
    if str(n) in icmp_seq_v2v_7_:
        icmp_seq_v2v_7.append(int(icmp_seq_v2v_7_[id]))
        latency_no_controller_7.append(float(latency_no_controller_7_[id]))
        id += 1
    else:
        icmp_seq_v2v_7.append(float(n))
        latency_no_controller_7.append(None)

id = 0
for n in range(0, x_limit):
    if str(n) in icmp_seq_:
        icmp_seq.append(int(icmp_seq_[id]))
        latency.append(float(latency_[id]))
        id += 1
    else:
        icmp_seq.append(n)
        latency.append(None)

icmp_seq_v2v.pop()
latency_no_controller.pop()
icmp_seq_v2v_7.pop()
latency_no_controller_7.pop()
icmp_seq.pop()
latency.pop()

x = np.array((latency_no_controller + latency_no_controller_7 + latency), dtype=np.float64)
max_list = np.nanmax(x)  #int(max(latency_rssid + latency)
max_y_d = max_list + 5
max_y_d_txt = max_list + 9
max_y_c = max_list + 15
max_y_c_txt = max_list + 19
y_lim = max_list + 45

fig, ax1 = plt.subplots()
fig_name = "latency-adhoc.eps"

Data = {'latency_no_controller': latency_no_controller,
        'icmp_seq_v2v': icmp_seq_v2v,
        'latency_no_controller_7': latency_no_controller_7,
        'icmp_seq_v2v_7': icmp_seq_v2v_7,
        'icmp_seq': icmp_seq,
        'latency': latency
       }

df = DataFrame(Data, columns=['latency_no_controller', 'icmp_seq_v2v', 'latency_no_controller_7', 'icmp_seq_v2v_7', 'latency', 'icmp_seq'])
colors = ['dodgerblue', 'orangered', 'black']

# gca stands for 'get current axis'
ax = plt.gca()

i = 0
for loss in df['latency_no_controller']:
    if math.isnan(loss):
        i += 1
n_no_controller = "%.2f" % ((i * 100) / len(df))
i = 0
for loss in df['latency_no_controller_7']:
    if math.isnan(loss):
        i += 1
n_no_controller_7 = "%.2f" % ((i * 100) / len(df))
i = 0
for loss in df['latency']:
    if math.isnan(loss):
        i += 1
n_controller = "%.2f" % ((i * 100) / len(df))

df.plot(kind='line', x='icmp_seq', y='latency', color=colors[0], ax=ax, label='D4')
df.plot(kind='line', ls='--', x='icmp_seq_v2v', y='latency_no_controller', color=colors[1], ax=ax, label='Without controller (gw = 2)')
df.plot(kind='line', ls='dashdot', x='icmp_seq_v2v_7', y='latency_no_controller_7', color=colors[2], ax=ax, label='Without controller (gw = 7)')
ax.set_xlim([0, x_limit])
ax.annotate("%s%% packet loss" % n_no_controller, xy=(80, 450),
            xycoords='data', va='top', ha='left', fontsize=10, color=colors[1],
            xytext=(0, 0), textcoords='offset points')
ax.annotate("%s%% packet loss" % n_no_controller_7, xy=(80, 450),
            xycoords='data', va='top', ha='left', fontsize=10, color=colors[2],
            xytext=(0, 0), textcoords='offset points')
ax.annotate("%s%% packet loss" % n_controller, xy=(80, 480),
            xycoords='data', va='top', ha='left', fontsize=10, color=colors[0],
            xytext=(0, 0), textcoords='offset points')

"""
enb1_d_pos = [0, 15]
enb2_d_pos = [31, 100]
enb3_d_pos = [173, 254]
v2v_d_pos = [16, 100]

enb1_c_pos = [0, 30]
enb2_c_pos = [110, 173]
enb3_c_pos = [173, 254]


ax.annotate('', xy=(enb1_d_pos[0], max_y_d), xytext=(enb1_d_pos[1], max_y_d),
            arrowprops={'arrowstyle': '<->', "linestyle" : "--", 'color':color[0]}, va='center', multialignment='center', ha='center')
ax.text((((enb1_d_pos[1]-enb1_d_pos[0])/2)+enb1_d_pos[0]), max_y_d_txt, "enb1", ha="center", va="center", size=12, color=color[0])

ax.annotate('', xy=(v2v_d_pos[0], max_y_d), xytext=(v2v_d_pos[1], max_y_d),
            arrowprops={'arrowstyle': '<->', "linestyle" : "--", 'color':color[0]}, va='center', multialignment='center', ha='center')
ax.text((((v2v_d_pos[1]-v2v_d_pos[0])/2)+v2v_d_pos[0]), max_y_d_txt, "v2v", ha="center", va="center", size=12, color=color[0])

ax.annotate('', xy=(enb1_c_pos[0], max_y_c), xytext=(enb1_c_pos[1], max_y_c),
            arrowprops={'arrowstyle': '<->', 'color':color[1]}, va='center', multialignment='center', ha='center')
ax.text((((enb1_c_pos[1]-enb1_c_pos[0])/2)+enb1_c_pos[0]), max_y_c_txt, "enb1", ha="center", va="center", size=12, color=color[1])
"""

ax.set_ylim([15, y_lim])
ax.set_xlabel("Time (s)", fontsize=15)
ax.set_ylabel("Latency (ms)", fontsize=15)

plt.savefig(fig_name)
