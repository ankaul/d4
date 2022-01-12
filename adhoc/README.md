# Handover Scenario

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
~$ git clone https://github.com/intrig-unicamp/mininet-wifi   
~$ cd mininet-wifi    
~/mininet-wifi$ sudo util/install.sh -WlnfvBP  
~/mininet-wifi$ cp ../d2-its-mininet-wifi/adhoc/new-york.net.xml mn_wifi/sumo/data/
~/mininet-wifi$ cp ../d2-its-mininet-wifi/adhoc/new-york.rou.xml mn_wifi/sumo/data/
~/mininet-wifi$ sudo make install
```

#### copy mininet-wifi dir to /root
`cp -r mininet-wifi /root`  


## Running the code   

###  Simulating the Adhoc scenario
**No-controller scenario**:    

When car2 is the gateway
```
sudo python adhoc-topo.py no-controller 2
```


When car7 is the gateway
```
sudo python adhoc-topo.py no-controller 7
```

**With-controller scenario**:
```
sudo python adhoc-topo.py controller
```

## Generating the graph
```
sudo python pandas-adhoc.py   
```

See the results through the `load-results.eps` file.

# Note
You may need to add the content below into `/etc/NetworkManager/NetworkManager.conf` if you have _Network Manager_ running.

```
[device]
wifi.scan-rand-mac-address=no
```
