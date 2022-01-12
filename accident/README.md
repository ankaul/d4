# Accident Scenario

## Requirements 
- **Kernel version**: + v5.8-rc1 (IEEE 802.11p support)
- **wireless-regdb and CRDA**: See https://mininet-wifi.github.io/80211p/ for 802.11p support. In general, if you can establish communication between sta1 and sta2 by running https://github.com/intrig-unicamp/mininet-wifi/blob/master/examples/ieee80211p.py this seems that everything is ok with 802.11p.
- **python 2**: Due to the requirements for the wireless-regdb from the repository above 
- **mininet-wifi**: emulation platform  
- **p4**: for P4-enabled APs   
- **sumo and sumo-tools (tested with 1.6)**: vehicular simulation
- **python-scapy**: packet sniffer
- **mosquitto, mosquitto-client and paho-mqtt**: MQTT communication
- **python-pandas**: graph generation 
- **bridge-utils**: create the virtual interface used by the socket communication
  
### Installing Mininet-WiFi  
```
~/d2-its-mininet-wifi$ git clone https://github.com/intrig-unicamp/mininet-wifi   
~/d2-its-mininet-wifi$ cd mininet-wifi    
~/d2-its-mininet-wifi/mininet-wifi$ sudo util/install.sh -WlnfvB  
```

### Replacing net file in order to run the experiment without TLS

```
~/d2-its-mininet-wifi/mininet-wifi$ cp ../new-york.net.xml mn_wifi/sumo/data
~/d2-its-mininet-wifi/mininet-wifi$ sudo make install
``` 

#### copy mininet-wifi dir to /root
`cp -r mininet-wifi /root`  

## Running the code   
###  Simulating an accident
**No-Accident scenario**:    
```
~/d2-its-mininet-wifi/emergency$ sudo python emergency-topo.py no_accident
```

**Centralized scenario**:    
```
~/d2-its-mininet-wifi/emergency$ sudo python emergency-topo.py centralized
```

**Distributed scenario**:
```
~/d2-its-mininet-wifi/emergency$ sudo python emergency-topo.py distributed
```

**Distributed scenario (100ms delayed)**:
```
~/d2-its-mininet-wifi/emergency$ sudo python emergency-topo.py distributed 0.1
```

**Generating the graph**:
```
~/d2-its-mininet-wifi/emergency$ sudo python pandas-accident.py   
```

See the results through the `accident-results.eps` file.

# Note
You may need to add the content below into `/etc/NetworkManager/NetworkManager.conf` if you have _Network Manager_ running.

```
[device]
wifi.scan-rand-mac-address=no
```
