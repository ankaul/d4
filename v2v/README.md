# V2V Scenario

## Requirements 
- **Kernel version**: + v5.8-rc1 (IEEE 802.11p support)
- **wireless-regdb and CRDA**: See https://mininet-wifi.github.io/80211p/ for 802.11p support
- **mininet-wifi**: emulation platform  
- **p4**: for P4-enabled APs
- **sumo and sumo-tools (tested with 1.6)**: vehicular simulation
- **python-scapy**: packet sniffer
- **mosquitto, mosquitto-client and paho-mqtt**: MQTT communication
- **python-pandas**: graph generation 
- **bridge-utils**: create the virtual interface used by the socket communication

  
### Installing Mininet-WiFi  
```
git clone https://github.com/intrig-unicamp/mininet-wifi   
cd mininet-wifi    
sudo util/install.sh -WlnfvBP  
```

#### copy mininet-wifi dir to /root
`$ cp -r mininet-wifi /root`  

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
