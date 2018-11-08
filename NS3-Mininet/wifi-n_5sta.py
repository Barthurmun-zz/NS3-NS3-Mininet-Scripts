from mininet.net import Mininet
from mininet.node import Node, Switch
from mininet.link import Link, Intf
from mininet.log import setLogLevel, info
from mininet.cli import CLI

import mininet.ns3
from mininet.ns3 import WIFISegment
import ns.applications
import ns.core
import ns.wifi

import sys
import argparse

def Main():
    parser = argparse.ArgumentParser(description='802.11n mininet-ns3 scenario')
    parser.add_argument('-g', '--GI', help='Setting Guard Interval', action='store_true', default=False)
    parser.add_argument('-b', '--BANDWIDTH', help='Set bandwidth', default=20, type = int)
    parser.add_argument('-m', '--MCS', help='Setting MCS', default=2, type = int)
    parser.add_argument('-u', '--UDP', help='Turning off UDP protocol', action='store_false', default=True)
    parser.add_argument('-t', '--TP', help='Setting client throughout', default=20, type = float)
    parser.add_argument('-p', '--PCAP', help='Enable Pcap collection', action='store_true', default=False)
    
    args = parser.parse_args()

    Start(args.GI, args.MCS, args.BANDWIDTH, args.UDP, args.TP, args.PCAP)
    
def Start(GI=False, MCS=2, Bandwidth=20, UDP=True, TP=20, PCAP=False):
    setLogLevel( 'info' )
    #info( '*** ns-3 network demo\n' )
    net = Mininet()

    #info( '*** Creating Network\n' )
    h0 = net.addHost( 'h0' )
    h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )
    h3 = net.addHost( 'h3' )
    h4 = net.addHost( 'h4' )
    h5 = net.addHost( 'h5' )

    wifi = WIFISegment()

    #CONFIGURATION
    udp = UDP
    gi = GI #0,1
    bandwidth = Bandwidth #20,40,80
    mcs = MCS #2,4,7
 
    if udp == False:
        #TCP
        payloadSize = 1448  #bytes
        ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (payloadSize))
    else:
        payloadSize = 1472

    wifi.wifihelper.SetStandard(ns.wifi.WIFI_PHY_STANDARD_80211n_5GHZ)

    # Enabling Shor guard intervals:
    wifi.phyhelper.Set("ShortGuardEnabled", ns.core.BooleanValue(gi))
    
    wifi.machelper = ns.wifi.HtWifiMacHelper.Default ()
    
    DataRate = ns.wifi.HtWifiMacHelper.DataRateForMcs (mcs)
    #DataRate = ns.core.StringValue ("HtMcs14")
    
    # set datarate for node h0
    wifi.wifihelper.SetRemoteStationManager( "ns3::ConstantRateWifiManager",
                                             "DataMode", DataRate, "ControlMode", ns.wifi.HtWifiMacHelper.DataRateForMcs (0) )
      
    Sssid = "wifi-80211n"
    wifi.addSta( h0, ssid=Sssid )
    wifi.addSta( h1, ssid=Sssid )
    wifi.addSta( h2, ssid=Sssid )
    wifi.addSta( h3, ssid=Sssid )
    wifi.addSta( h4, ssid=Sssid )
    wifi.addAp( h5, ssid=Sssid  )

    # set channel bandwidth
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (bandwidth))
    
    if PCAP == True:
        wifi.phyhelper.EnablePcap( "80211acCA_Sta1.pcap", h0.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211acCA_Sta2.pcap", h1.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211acCA_Sta3.pcap", h2.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211acCA_Sta4.pcap", h3.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211acCA_Sta5.pcap", h4.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211acCA_Ap.pcap", h5.nsNode.GetDevice( 0 ), True, True );
   
    #info( '*** Configuring hosts\n' )
    h0.setIP('192.168.123.1/24')
    h1.setIP('192.168.123.2/24')
    h2.setIP('192.168.123.3/24')
    h3.setIP('192.168.123.4/24')
    h4.setIP('192.168.123.5/24')
    h5.setIP('192.168.123.6/24')

    mininet.ns3.start()

   
    #info( '\n *** Testing network connectivity\n' )
    net.pingFull([h0,h5])
    #net.pingFull([h1,h2])
    #net.pingFull([h0,h1])
    info('*** Starting UDP iperf server on AP(h5)\n')
    h5.sendCmd( "iperf -s -i 1 -u" )
    info( '*** Testing bandwidth between h0 and h5 none is transmitting\n' )
    val = "iperf -c 192.168.123.6 -u -b "+str(TP)+"M"
    h0.cmdPrint(val)
    info( '*** Testing bandwidth between h0 and h5 while everyone transmitting\n' )
    val = "iperf -c 192.168.123.6 -u -b "+str(TP)+"M"
    h0.sendCmd(val)
    h1.sendCmd(val)
    h2.sendCmd(val)
    h3.sendCmd(val)
    h4.cmdPrint(val)
    #CLI(net)


if __name__ == '__main__':
    Main()

    

