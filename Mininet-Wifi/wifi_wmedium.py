#!/usr/bin/python

'This example runs stations in AP mode'

import sys

from mininet.node import Controller
from mn_wifi.node import UserAP
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference


def topology():
    'Create a network.'
    #Question 2:
    # net = Mininet_wifi(controller=Controller, link=wmediumd, accessPoint=UserAP,
    #                    wmediumd_mode=interference, inNamespace=True,
    #                    noise_threshold=-91, fading_coefficient=0)
    
    net = Mininet_wifi(controller=Controller, link=wmediumd,
                       wmediumd_mode=interference,
                       noise_threshold=-91, fading_coefficient=0)
    

    info("*** Creating nodes\n")
    #Question 1:
    # ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='ac', channel='36', hw_mode='a', vht_capab="[VHT160][SHORT-GI-160][MAX-AMPDU-7991]",
    #                             position='15,30,0' )
    # # Question 4:
    # ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='n', channel='36', band='5', ht_capab="[HT40+][SHORT-GI-40]", position='15,30,0' )
    
    ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='a', channel='36', position='15,30,0' )
    
    sta1 = net.addStation('sta1', mac='00:00:00:00:00:02',
                            ip='192.168.0.2/24', position='15,32,0')
    sta2 = net.addStation('sta2', mac='00:00:00:00:00:04',
                            ip='192.168.0.3/24', position='15,32,0')  
    sta3 = net.addStation('sta3', mac='00:00:00:00:00:06',
                            ip='192.168.0.4/24', position='15,32,0')  
    sta4 = net.addStation('sta4', mac='00:00:00:00:00:08',
                            ip='192.168.0.5/24', position='15,32,0')  
    sta5 = net.addStation('sta5', mac='00:00:00:00:00:10',
                            ip='192.168.0.6/24', position='15,32,0')  
    
    h1 = net.addHost('h1', ip='192.168.0.10/24')

     #Question 3:                        
    # sta3 = net.addStation('sta3', mac='00:00:00:00:00:06',
    #                         ip='192.168.0.4/24', position='20,50,0')   
    # #                        
    c1 = net.addController('c1')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4)

    info("***Ploting the graph***\n")
    net.plotGraph(max_x=100, max_y=100)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    #ap1.setMasterMode(intf='ap1-wlan0', ssid='ap1-ssid', channel='8', mode='a')
   
    info("*** Adding Link\n")
    net.addLink(ap1, sta1) 
    net.addLink(ap1, sta2)
    net.addLink(ap1, sta3) 
    net.addLink(ap1, sta4)
    net.addLink(ap1, sta5) 
    net.addLink(h1,ap1)
    #net.addLink(ap1, sta3) 

    info("*** Starting network\n")
    net.build()
    c1.start()
    ap1.start([c1])

    info("*** Running CLI\n")
    # sta1.sendCmd('iw dev sta1-wlan0 set bitrates legacy-5 24 36 48 ht-mcs-2.4 lgi-2.4')
    # sta2.sendCmd('iperf -s -u')
    # info("BUKAKA\n")
    # sta1.cmdPrint('iperf -c 192.168.0.3 -u -b 21M')
    # sta1.cmdPrint('ping 192.168.0.3 -c 5')
    # sta1.sendCmd('iw dev sta1-wlan0 set bitrates legacy-5 24 ht-mcs-2.4 lgi-2.4')
    # sta1.cmdPrint('iperf -c 192.168.0.3 -u -b 15M')
    # sta1.cmdPrint('ping 192.168.0.3 -c 5')
    # sta1.sendCmd('iw dev sta1-wlan0 set bitrates legacy-5 6 9 ht-mcs-2.4 lgi-2.4')
    # sta1.cmdPrint('iperf -c 192.168.0.3 -u -b 9M')
    # sta1.cmdPrint('ping 192.168.0.3 -c 5')
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()

