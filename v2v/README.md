# V2V Scenario

## Requirements 
- **Kernel version**: + v5.8-rc1 (IEEE 802.11p support)
- **[wireless-regdb and CRDA](https://mininet-wifi.github.io/80211p/)**: In general, if you can establish communication between sta1 and sta2 by running https://github.com/intrig-unicamp/mininet-wifi/blob/master/examples/ieee80211p.py this means that IEEE 802.11p is working.
- **[Python 2](https://www.python.org/download/releases/2.0/)**: Due to the requirements for the `wireless-regdb` package from the repository above 
- **[Mininet-WiFi](https://github.com/intrig-unicamp/mininet-wifi)**: Emulation platform  
- **[P4](https://opennetworking.org/p4/)**: For P4-enabled APs. P4 dependencies can be installed by using the `-P` flag as suggested by https://github.com/intrig-unicamp/mininet-wifi#installation
- **[sumo and sumo-tools (tested with 1.6)](https://www.eclipse.org/sumo/)**: For vehicular simulation
- **[python-scapy](https://scapy.net/)**: Packet sniffer
- **[mosquitto, mosquitto-client and paho-mqtt](https://mosquitto.org/)**: MQTT communication
- **[python-pandas](https://pandas.pydata.org/)**: For graph generation 
- **[bridge-utils](https://wiki.debian.org/BridgeNetworkConnections)**: Responsible for creating the virtual interface used by the socket communication


#### copy mininet-wifi dir to /root
`$ cp -r mininet-wifi /root`  

This is necessary because `xterm` will be opened with root user

## Running the code   

###  Simulating the V2V scenario
**Centralized scenario**:    
```
sudo python v2v-topo.py centralized
```

**Distributed scenario**:
```
sudo python v2v-topo.py distributed
```

## Generating the graph
```
sudo python pandas-v2v.py   
```

See the results through the `load-results.eps` file.

# Note
You may need to add the content below into `/etc/NetworkManager/NetworkManager.conf` if you have _Network Manager_ running.

```
[device]
wifi.scan-rand-mac-address=no
```
