#!/usr/bin/env python

from pandas import DataFrame

import subprocess
import numpy as np
import matplotlib.pyplot as plt
import numpy as np

file1 = 'ping-distributed.txt'
file2 = 'ping-centralized.txt'

latency_v2v = 'grep -r \"ms\" %s | awk \'{print $7}\' | tr -d \"time=\"' % file1
icmp_seq_v2v = 'grep -r \"ms\" %s | awk \'{print $5}\' | tr -d "icmp_seq="' % file1
latency = 'grep -r \"ms\" %s | awk \'{print $7}\' | tr -d \"time=\"' % file2
icmp_seq = 'grep -r \"ms\" %s | awk \'{print $5}\' | tr -d "icmp_seq="' % file2


address = subprocess.Popen(latency, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
latency_ = out.decode().split('\n')

address = subprocess.Popen(icmp_seq, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
icmp_seq_ = out.decode().split('\n')

address = subprocess.Popen(latency_v2v, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
latency_v2v_ = out.decode().split('\n')

address = subprocess.Popen(icmp_seq_v2v, stdout=subprocess.PIPE, shell=True)
(out, err) = address.communicate()
icmp_seq_v2v_ = out.decode().split('\n')


latency_v2v = []
icmp_seq_v2v = []
latency = []
icmp_seq = []

id = 0
for n in range(0, 101):
    if str(n) in icmp_seq_v2v_:
        icmp_seq_v2v.append(int(icmp_seq_v2v_[id]))
        latency_v2v.append(float(latency_v2v_[id]))
        id += 1
    else:
        icmp_seq_v2v.append(float(n))
        latency_v2v.append(None)

id = 0
for n in range(0, 101):
    if str(n) in icmp_seq_:
        icmp_seq.append(int(icmp_seq_[id]))
        latency.append(float(latency_[id]))
        id += 1
    else:
        icmp_seq.append(n)
        latency.append(None)

icmp_seq_v2v.pop()
latency_v2v.pop()
icmp_seq.pop()
latency.pop()

x = np.array((latency_v2v + latency), dtype=np.float64)
max_list = np.nanmax(x)  #int(max(latency_rssid + latency)
max_y_d = max_list + 5
max_y_d_txt = max_list + 9
max_y_c = max_list + 15
max_y_c_txt = max_list + 19
y_lim = max_list + 45

fig, ax1 = plt.subplots()
fig_name = "latency-v2v.eps"

Data = {'latency_v2v': latency_v2v,
        'icmp_seq_v2v': icmp_seq_v2v,
        'icmp_seq': icmp_seq,
        'latency': latency
       }

df = DataFrame(Data, columns=['latency_v2v', 'icmp_seq_v2v', 'latency', 'icmp_seq'])
color = ['dodgerblue', 'orangered']

# gca stands for 'get current axis'
ax = plt.gca()

df.plot(kind='line', ls='--', x='icmp_seq_v2v', y='latency_v2v', color=color[0], ax=ax, label='V2V Scenario')
df.plot(kind='line', x='icmp_seq', y='latency', color=color[1], ax=ax, label='Infra Scenario (only)')
ax.annotate('transition to V2V', xy =(110, 326), xytext=(20, 260), arrowprops=dict(color=color[0], lw=4, arrowstyle='->'))

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


ax.set_ylim([15, y_lim])
ax.set_xlabel("Time (s)", fontsize=15)
ax.set_ylabel("Latency (ms)", fontsize=15)

plt.savefig(fig_name)
