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
    parser = argparse.ArgumentParser(description='802.11a mininet-ns3 scenario')
    parser.add_argument('-or', '--OFDMRate', help='Setting OFDMRate', default=9, type = int)
    parser.add_argument('-tcp', '--UDP', help='Turning off UDP protocol', action='store_false', default=True)
    parser.add_argument('-t', '--TP', help='Setting client throughout', default=9, type = float)
    parser.add_argument('-p', '--PCAP', help='Enable Pcap collection', action='store_true', default=False)
    
    args = parser.parse_args()

    Start(args.OFDMRate, args.UDP, args.TP, args.PCAP)

def Start(OFDM_R=9, UDP=True, TP=20, PCAP=False):
    setLogLevel( 'info' )
    #info( '*** ns-3 network demo\n' )
    net = Mininet()

    #info( '*** Creating Network\n' )
    h0 = net.addHost( 'h0' )
    #h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )

    wifi = WIFISegment()

    #CONFIGURATION
    udp = UDP
    bandwidth = 20 #20
    ofdm_r = "OfdmRate"+str(OFDM_R)+"Mbps"
    OfdmRate = ofdm_r #9,24,48
    if udp == False:
        #TCP
        payloadSize = 1448  #bytes
        ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (payloadSize))
    else:
        payloadSize = 1472

    info( '*** Creating Network\n' )
    h0 = net.addHost( 'h0' )
    #h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )

    wifi = WIFISegment()

    wifi.wifihelper.SetStandard(ns.wifi.WIFI_PHY_STANDARD_80211a)
  
    wifi.wifihelper.SetRemoteStationManager( "ns3::ConstantRateWifiManager",
                                             "DataMode", ns.core.StringValue (OfdmRate), "ControlMode", ns.core.StringValue ("OfdmRate9Mbps") )
    
    Sssid = "wifi-80211a"

    wifi.addSta( h0, ssid=Sssid )

    wifi.addAp( h2, ssid=Sssid  )

    # set channel bandwidth
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (bandwidth))
    
    if PCAP == True:
        wifi.phyhelper.EnablePcap( "80211a_sta1.pcap", h0.nsNode.GetDevice( 0 ), True, True );
        #wifi.phyhelper.EnablePcap( "80211a_sta2.pcap", h1.nsNode.GetDevice( 0 ), True, True );
        wifi.phyhelper.EnablePcap( "80211a_ap.pcap", h2.nsNode.GetDevice( 0 ), True, True );

    #info( '*** Configuring hosts\n' )
    h0.setIP('192.168.123.1/24')
    #h1.setIP('192.168.123.2/24')
    h2.setIP('192.168.123.3/24')

    mininet.ns3.start()

    #info( '\n *** Testing network connectivity\n' )
    net.pingFull([h0,h2])
    info( '*** Testing bandwidth between h0 and h2 while h1 is not transmitting\n' )
    h2.sendCmd( "iperf -s -i 1 -u" )
    val = "iperf -c 192.168.123.3 -u -b "+str(TP)+"M"
    h0.cmdPrint(val)
    
    #CLI(net)
   
    
if __name__ == '__main__':
    Main()
