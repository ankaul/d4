# Accident Scenario

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
  

### Replacing net file in order to run the experiment without TLS

```
~/d2-its-mininet-wifi/mininet-wifi$ cp ../new-york.net.xml mn_wifi/sumo/data
~/d2-its-mininet-wifi/mininet-wifi$ sudo make install
``` 

#### copy mininet-wifi dir to /root
`cp -r mininet-wifi /root`  

This is necessary because `xterm` will be opened with root user


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
