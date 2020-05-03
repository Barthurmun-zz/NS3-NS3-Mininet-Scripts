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
import ns.flow_monitor
import sys
import argparse
import time


def Main():
    parser = argparse.ArgumentParser(description='802.11ac mininet-ns3 scenario')
    parser.add_argument('-g', '--GI', help='Setting Guard Interval', action='store_true', default=False)
    parser.add_argument('-b', '--BANDWIDTH', help='Set bandwidth', default=20, type = int)
    parser.add_argument('-m', '--MCS', help='Setting MCS', default=2, type = int)
    parser.add_argument('-u', '--UDP', help='Turning off UDP protocol', action='store_false', default=True)
    parser.add_argument('-t', '--TP', help='Setting client throughout', default=19, type = float)
    parser.add_argument('-p', '--PCAP', help='Enable Pcap collection', action='store_true', default=False)
    
    args = parser.parse_args()

    Start(args.GI, args.MCS, args.BANDWIDTH, args.UDP, args.TP, args.PCAP)
    
def Start(GI=False, MCS=2, Bandwidth=20, UDP=True, TP=20, PCAP=False):
    setLogLevel( 'info' )
    #info( '*** ns-3 network demo\n' )
    net = Mininet()

    #info( '*** Creating Network\n' )
    h0 = net.addHost( 'h0')
    #h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2')

    wifi = WIFISegment()

    #CONFIGURATION
    udp = UDP
    gi = GI #0,1
    bandwidth = Bandwidth #20,40,80
    mcs = MCS #2,4,7
    
    # if udp == False:
    #     #TCP
    #     payloadSize = 1448  #bytes
    #     ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (payloadSize))
    # else:
    #     payloadSize = 1472

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

    mininet.ns3.setPosition( h0, 10.0, 10.0, 0.0)
    mininet.ns3.setPosition( h2, 5.0, 5.0, 0.0)

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
    
    h0.cmd("ifconfig h0-eth0 mtu 9000 ")
    h2.cmd("ifconfig h2-eth0 mtu 9000 ")

    info( '*** Testing network connectivity \n' )
    h0.cmdPrint("ping 192.168.123.3 -c 3")

    info( '*** Testing network connectivity\n' )
    h0.cmd("tcpdump -i h0-eth0 -w h0_test.pcap & ")
    h2.cmd("tcpdump -i h2-eth0 -w h2_test.pcap & ")

    info( '*** Testing bandwidth between h0 and h2 \n' )
    h2.cmd( "iperf -s -u -p 5003 & " )
    val = "iperf -c 192.168.123.3 -u -l 1400 -p 5003 -b "+str(TP)+"M"
    h0.cmdPrint(val)

    # #Alternative method of sending and seving iperf traffic results
    # h2.cmd("iperf -s -i 1 -u > AP_AC_1STA_log.txt &")
    # val = val + " &"
    # h0.cmd(val)
    
    info( '***Position of our architecture***\n')
    info( 'STA:', mininet.ns3.getPosition( h0 ), '\n')
    info( 'AP:', mininet.ns3.getPosition( h2 ), '\n')

    #STREAMING USING RSTP !!!!:

    # info( '**Streaming of Video 1 from AP to STA***\n')
    # h2.cmd( " $(echo Y3ZsYyBmaWxlOi8vL2hvbWUvb3Nib3hlcy9Eb3dubG9hZHMvZmlsZV9leGFtcGxlX01QNF8xOTIwXzE4TUcubXA0IC0tc291dD0jcnRwe3NkcD1ydHNwOi8vOjg1NTQvc3RyZWFtfSAtLXNvdXQtYWxsIC0tc291dC1rZWVwCg== | base64 -d) &")    
    
    info( '**Streaming of Video 2 from AP to STA***\n')
    h2.cmd( " $(echo Y3ZsYyBmaWxlOi8vL2hvbWUvb3Nib3hlcy9Eb3dubG9hZHMvUGFuYXNvbmljX0hEQ19UTV83MDBfUF81MGkubXA0IC0tc291dD0jcnRwe3NkcD1ydHNwOi8vOjg1NTQvc3RyZWFtfSAtLXNvdXQtYWxsIC0tc291dC1rZWVwIAo= | base64 -d) &")    
    
    # info( '**Streaming of Video Bunny Rabbit in NQ from AP to STA***\n')
    # h2.cmd( " $(echo Y3ZsYyBmaWxlOi8vL2hvbWUvb3Nib3hlcy9Eb3dubG9hZHMvYmJiX3N1bmZsb3dlcl8xMDgwcF82MGZwc19ub3JtYWwubXA0IC0tc291dD0jcnRwe3NkcD1ydHNwOi8vOjg1NTQvc3RyZWFtfSAtLXNvdXQtYWxsIC0tc291dC1rZWVwCg== | base64 -d) &")    
    
    # info( '**Streaming of Video Bunny Rabbit in HQ from AP to STA***\n')
    # h2.cmd( " $(echo Y3ZsYyBmaWxlOi8vL2hvbWUvb3Nib3hlcy9Eb3dubG9hZHMvYmJiX3N1bmZsb3dlcl8yMTYwcF82MGZwc19ub3JtYWwubXA0IC0tc291dD0jcnRwe3NkcD1ydHNwOi8vOjg1NTQvc3RyZWFtfSAtLXNvdXQtYWxsIC0tc291dC1rZWVwCg== | base64 -d) &")    
    
    time.sleep(1)
    
    info( '**Opening RSTP stream on STA***\n')
    #Use h0 vlc-wrapper to open VLC on host 0
    h0.cmdPrint( "cvlc rtsp://192.168.123.3:8554/stream &")
    
    #info("***Running CLI\n")
    #CLI(net)
    
    info( '**Transmission will take 45s***\n')
    time.sleep(45)
    
    #STREAMING USING RTP !!!!:
     
    # #Use h0 vlc-wrapper to open VLC on host 0
    # h0.cmdPrint( "cvlc rtp://@:5004 &")
    # time.sleep(1)
    
    # #CVLC Streaming Video 1:                                                                                                                                                                                                                         
    # #h2.cmdPrint( "$(echo Y3ZsYyBmaWxlOi8vL2hvbWUvb3Nib3hlcy9Eb3dubG9hZHMvZmlsZV9leGFtcGxlX01QNF8xOTIwXzE4TUcubXA0IC0tc291dD0jcnRwe2RzdD0xOTIuMTY4LjEyMy4xLHBvcnQ9NTAwNCxtdXg9dHMsc2FwLG5hbWU9VmlkZW8xfSAtLW5vLXNvdXQtYWxsIC0tc291dC1rZWVwCg== | base64 -d) &")
    # #h2.cmdPrint( "cvlc file:///home/osboxes/Downloads/file_example_MP4_1920_18MG.mp4 --sout=#rtp{dst=192.168.123.1,port=5004,mux=ts,sap,name=Video1} --no-sout-all --sout-keep &")
    
    # #CVLC Streaming Video 2:                                                                                                                                                                                                                         
    # h2.cmdPrint( "$(echo Y3ZsYyBmaWxlOi8vL2hvbWUvb3Nib3hlcy9Eb3dubG9hZHMvUGFuYXNvbmljX0hEQ19UTV83MDBfUF81MGkubXA0IC0tc291dD0jcnRwe2RzdD0xOTIuMTY4LjEyMy4xLHBvcnQ9NTAwNCxtdXg9dHMsc2FwLG5hbWU9VmlkZW8xfSAtLW5vLXNvdXQtYWxsIC0tc291dC1rZWVwCg== | base64 -d) &")


    info("***Ending TCPDump and cleaning up***\n")
    h0.cmd("killall tcpdump")
    h2.cmd("killall tcpdump")
    h0.cmd("pkill -9 vlc")
    h2.cmd("pkill -9 vlc")

    mininet.ns3.stop()      
    mininet.ns3.clear()
    net.stop()

if __name__ == '__main__':
    Main()

