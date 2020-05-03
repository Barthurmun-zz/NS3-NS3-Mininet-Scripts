#Author: Jakub Bryl

from mininet.net import Mininet
from mininet.node import Node, Switch
from mininet.link import Link, Intf
from mininet.log import setLogLevel, info
from mininet.cli import CLI

import mininet.ns3
from mininet.ns3 import WIFISegment

import ns.core
import ns.wifi
import sys
import argparse

def Main():
    parser = argparse.ArgumentParser(description='802.11ac mininet-ns3 scenario')
    parser.add_argument('-g', '--GI', help='Setting Guard Interval', action='store_true', default=False)
    parser.add_argument('-b', '--BANDWIDTH', help='Set bandwidth', default=20, type = int)
    parser.add_argument('-m', '--MCS', help='Setting MCS', default=4, type = int)
    parser.add_argument('-u', '--UDP', help='Turning off UDP protocol', action='store_false', default=True)
    parser.add_argument('-t', '--TP', help='Setting client throughout', default=36, type = float)
    parser.add_argument('-p', '--PCAP', help='Enable Pcap collection', action='store_true', default=False)
    
    args = parser.parse_args()

    Start(args.GI, args.MCS, args.BANDWIDTH, args.UDP, args.TP, args.PCAP)
    
def Start(GI=False, MCS=2, Bandwidth=20, UDP=True, TP=20, PCAP=False):
    setLogLevel( 'info' )
    #info( '*** ns-3 network demo\n' )
    net = Mininet()

    #info( '*** Creating Network\n' )
    h0 = net.addHost( 'h0', position='10,10,0')
    #h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2', position='5,5,0')

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

    wifi.wifihelper.SetStandard(ns.wifi.WIFI_PHY_STANDARD_80211ac)

    # Enabling Shor guard intervals:
    wifi.phyhelper.Set("ShortGuardEnabled",ns.core.BooleanValue(gi))
    
    DataRate = "VhtMcs"+str(mcs)

    # set datarate for node h0
    wifi.wifihelper.SetRemoteStationManager( "ns3::ConstantRateWifiManager",
                                             "DataMode", ns.core.StringValue (DataRate), "ControlMode", ns.core.StringValue (DataRate) )
    
    wifi.machelper = ns.wifi.WifiMacHelper()
   
    Sssid = "wifi-80211ac"

    wifi.addSta( h0, ssid=Sssid)

    wifi.addAp( h2, ssid=Sssid)

    # set channel bandwidth
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (bandwidth))

    if PCAP == True:
        wifi.phyhelper.EnablePcap( "80211ac_Sta1.pcap", h0.nsNode.GetDevice( 0 ), True, True )
        #wifi.phyhelper.EnablePcap( "Ap-h1.pcap", h1.nsNode.GetDevice( 1 ), True, True );
        wifi.phyhelper.EnablePcap( "80211ac_Ap.pcap", h2.nsNode.GetDevice( 0 ), True, True )
   
    #info( '*** Configuring hosts\n' )
    h0.setIP('192.168.123.1/24')
    #h1.setIP('192.168.123.2/24')
    h2.setIP('192.168.123.3/24')

    mininet.ns3.start()

    #info( '\n *** Testing network connectivity\n' )
    h0.cmdPrint("ping 192.168.123.3 -c 3")
  
    info( '*** Testing bandwidth between h0 and h2 while h1 is not transmitting\n' )
    h2.sendCmd( "iperf -s -i 1 -u" )
    val = "iperf -c 192.168.123.3 -u -b "+str(TP)+"M"
    h0.cmdPrint(val)
    
    #Alternative method of sending and seving iperf traffic results
    #h2.cmd("iperf -s -i 1 -u > AP_AC_1STA_log.txt &")
    #val = val + " &"
    #h0.cmd(val)

    #VLC Player on STA
    #h2.cmdPrint("vlc-wrapper")
    #h0.sendCmd("vlc-wrapper &")
    

    #Use h0 vlc-wrapper to open VLC on host 0


    info("***Running CLI\n")
    CLI(net)

if __name__ == '__main__':
    Main()

