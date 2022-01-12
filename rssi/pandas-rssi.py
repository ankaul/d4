#!/usr/bin/env python

from pandas import DataFrame

import numpy as np
import subprocess
import matplotlib.pyplot as plt


file1 = 'ping-distributed.txt'
file2 = 'ping-centralized.txt'

latency_rssid = 'grep -r \"ms\" %s | awk \'{print $7}\' | tr -d \"time=\"' % file1
icmp_seq_rssid = 'grep -r \"ms\" %s | awk \'{print $5}\' | tr -d "icmp_seq="' % file1
latency = 'grep -r \"ms\" %s | awk \'{print $7}\' | tr -d \"time=\"' % file2
icmp_seq = 'grep -r \"ms\" %s | awk \'{print $5}\' | tr -d "icmp_seq="' % file2
color = ['dodgerblue', 'orangered']

address = subprocess.Popen(latency, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
latency_ = out.decode().split('\n')

address = subprocess.Popen(icmp_seq, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
icmp_seq_ = out.decode().split('\n')

address = subprocess.Popen(latency_rssid, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
latency_rssid_ = out.decode().split('\n')

address = subprocess.Popen(icmp_seq_rssid, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
icmp_seq_rssid_ = out.decode().split('\n')

latency_rssid = []
icmp_seq_rssid = []
latency = []
icmp_seq = []

id = 0
for n in range(0, 251):
    if str(n) in icmp_seq_rssid_:
        icmp_seq_rssid.append(float(icmp_seq_rssid_[id]))
        latency_rssid.append(float(latency_rssid_[id]))
        id += 1
    else:
        icmp_seq_rssid.append(float(n))
        latency_rssid.append(None)

id = 0
for n in range(0, 251):
    if str(n) in icmp_seq_:
        icmp_seq.append(float(icmp_seq_[id]))
        latency.append(float(latency_[id]))
        id += 1
    else:
        icmp_seq.append(float(n))
        latency.append(None)

icmp_seq_rssid.pop()
latency_rssid.pop()
icmp_seq.pop()
latency.pop()

x = np.array((latency_rssid + latency), dtype=np.float64)
max_list = np.nanmax(x)  #int(max(latency_rssid + latency))
max_y_d = max_list + 5
max_y_d_txt = max_list + 9
max_y_c = max_list + 15
max_y_c_txt = max_list + 19
y_lim = max_list + 45

fig, ax1 = plt.subplots()
fig_name = "latency-rssi.eps"

Data = {'latency_rssid': latency_rssid,
        'icmp_seq_rssid': icmp_seq_rssid,
        'icmp_seq': icmp_seq,
        'latency': latency
       }

df = DataFrame(Data,columns=['latency_rssid', 'icmp_seq_rssid', 'latency', 'icmp_seq'])


# gca stands for 'get current axis'
ax = plt.gca()

enb1_d_pos = [0, 122]
enb2_d_pos = [enb1_d_pos[1], 170]
enb3_d_pos = [enb2_d_pos[1], 254]

enb1_c_pos = [0, 142]
enb2_c_pos = [enb1_c_pos[1], 180]
enb3_c_pos = [enb2_c_pos[1], 254]

df.plot(kind='line', ls='--', x='icmp_seq_rssid', y='latency_rssid', color=color[0], ax=ax, label='Distributed Control')
df.plot(kind='line', x='icmp_seq', y='latency', color=color[1], ax=ax, label='Centralized Control')
ax.annotate('transition to V2V', xy=(110, 326), xytext=(20, 260), arrowprops=dict(color=color[0], lw=4, arrowstyle='->'))

ax.annotate('', xy=(enb1_d_pos[0], max_y_d), xytext=(enb1_d_pos[1], max_y_d),
            arrowprops={'arrowstyle': '<->', "linestyle" : "--", 'color':color[0]}, va='center', multialignment='center', ha='center')
ax.text((((enb1_d_pos[1]-enb1_d_pos[0])/2)+enb1_d_pos[0]), max_y_d_txt, "enb1", ha="center", va="center", size=12, color=color[0])

ax.annotate('', xy=(enb2_d_pos[0], max_y_d), xytext=(enb2_d_pos[1], max_y_d),
            arrowprops={'arrowstyle': '<->', "linestyle" : "--", 'color':color[0]}, va='center', multialignment='center', ha='center')
ax.text((((enb2_d_pos[1]-enb2_d_pos[0])/2)+enb2_d_pos[0]), max_y_d_txt, "enb2", ha="center", va="center", size=12, color=color[0])

ax.annotate('', xy=(enb3_d_pos[0], max_y_d), xytext=(enb3_d_pos[1], max_y_d),
            arrowprops={'arrowstyle': '<->', "linestyle" : "--", 'color':color[0]}, va='center', multialignment='center', ha='center')
ax.text((((enb3_d_pos[1]-enb3_d_pos[0])/2)+enb3_d_pos[0]), max_y_d_txt, "enb3", ha="center", va="center", size=12, color=color[0])


ax.annotate('', xy=(0, max_y_c), xytext=(enb1_c_pos[1], max_y_c),
            arrowprops={'arrowstyle': '<->', "linestyle" : "--", 'color':color[1]}, va='center', multialignment='center', ha='center')
ax.text((((enb1_c_pos[1]-enb1_c_pos[0])/2)+enb1_c_pos[0]), max_y_c_txt, "enb1", ha="center", va="center", size=12, color=color[1])

ax.annotate('', xy=(enb2_c_pos[0], max_y_c), xytext=(enb2_c_pos[1], max_y_c),
            arrowprops={'arrowstyle': '<->', "linestyle" : "--", 'color':color[1]}, va='center', multialignment='center', ha='center')
ax.text((((enb2_c_pos[1]-enb2_c_pos[0])/2)+enb2_c_pos[0]), max_y_c_txt, "enb2", ha="center", va="center", size=12, color=color[1])

ax.annotate('', xy=(enb3_c_pos[0], max_y_c), xytext=(enb3_c_pos[1], max_y_c),
            arrowprops={'arrowstyle': '<->', "linestyle" : "--", 'color':color[1]}, va='center', multialignment='center', ha='center')
ax.text((((enb3_c_pos[1]-enb3_c_pos[0])/2)+enb3_c_pos[0]), max_y_c_txt, "enb3", ha="center", va="center", size=12, color=color[1])


ax.set_ylim([15, y_lim])
ax.set_xlabel("Time (s)", fontsize=15)
ax.set_ylabel("Latency (ms)", fontsize=15)

plt.savefig(fig_name)
