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
import time

def Main():
    parser = argparse.ArgumentParser(description='802.11acCA mininet-ns3 scenario')
    parser.add_argument('-g', '--GI', help='Setting Guard Interval', action='store_true', default=False)
    parser.add_argument('-b', '--BANDWIDTH', help='Set bandwidth', default=40, type = int)
    parser.add_argument('-m', '--MCS', help='Setting MCS', default=3, type = int)
    parser.add_argument('-u', '--UDP', help='Turning off UDP protocol', action='store_false', default=True)
    parser.add_argument('-t', '--TP', help='Setting client throughout', default=54, type = float)
    parser.add_argument('-p', '--PCAP', help='Enable Pcap collection', action='store_true', default=False)
    
    args = parser.parse_args()

    Start(args.GI, args.MCS, args.BANDWIDTH, args.UDP, args.TP, args.PCAP)

def Start(GI=False, MCS=3, Bandwidth=40, UDP=True, TP=54, PCAP=False):
    setLogLevel( 'info' )
    #info( '*** ns-3 network demo\n' )
    net = Mininet()

    #info( '*** Creating Network\n' )
    h0 = net.addHost( 'h0' )
    #h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )
    h3 = net.addHost( 'h3' )
    h4 = net.addHost( 'h4' )
    #h5 = net.addHost( 'h5' )
    #h6 = net.addHost( 'h6' )
    h7 = net.addHost( 'h7' )
    h8 = net.addHost( 'h8' )

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
    wifi.phyhelper.Set("ShortGuardEnabled", ns.core.BooleanValue(gi))
    
    DataRate = "VhtMcs"+str(mcs)

    # set datarate for node h0
    wifi.wifihelper.SetRemoteStationManager( "ns3::ConstantRateWifiManager",
                                             "DataMode", ns.core.StringValue (DataRate), "ControlMode", ns.core.StringValue ("VhtMcs0") )
    
    wifi.machelper = ns.wifi.WifiMacHelper()
    
    #wifi.wifihelper.SetRemoteStationManager( "ns3::ConstantRateWifiManager",
    #                                         "DataMode", ns.core.StringValue ("VhtMcs8"), "ControlMode", ns.core.StringValue ("VhtMcs8") )
    
    Sssid = "wifi-80211acCA"
    
    wifi.addSta( h0,ext="ac", ssid=Sssid, port=9977, qosSupported=True)
    wifi.addSta( h3,ext="ac", ssid=Sssid, port=9998, qosSupported=True)
    wifi.addSta( h4,ext="ac", ssid=Sssid, port=9994, qosSupported=True)
    #wifi.addSta( h5,ext="ac", ssid=Sssid, port=9993, qosSupported=True)
    #wifi.addSta( h6,ext="ac", ssid=Sssid, port=9992, qosSupported=True)
    wifi.addSta( h7,ext="ac", ssid=Sssid, port=9977, qosSupported=True)
    wifi.addSta( h8,ext="ac", ssid=Sssid, port=9966, qosSupported=True)

    wifi.addAp( h2,ext="ac", ssid=Sssid, port=9999, qosSupported=True)
    
    # set channel bandwidth
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (bandwidth))
    
    if PCAP == True:
        wifi.phyhelper.SetPcapDataLinkType (ns.wifi.WifiPhyHelper.DLT_IEEE802_11_RADIO)
        wifi.phyhelper.EnablePcap( "80211ac_Sta1.pcap", h0.nsNode.GetDevice( 0 ), True, True );
        #wifi.phyhelper.EnablePcap( "Ap-h1.pcap", h1.nsNode.GetDevice( 1 ), True, True );
        wifi.phyhelper.EnablePcap( "80211ac_Ap.pcap", h2.nsNode.GetDevice( 0 ), True, True );
   
    #info( '*** Configuring hosts\n' )
    h0.setIP('192.168.123.1/24')
    h2.setIP('192.168.123.3/24')
    h3.setIP('192.168.123.4/24')
    h4.setIP('192.168.123.5/24')
    #h5.setIP('192.168.123.6/24')
    #h6.setIP('192.168.123.7/24')
    h7.setIP('192.168.123.8/24')
    h8.setIP('192.168.123.9/24')

    mininet.ns3.start()

    time.sleep(2)

    info( '\n *** Testing network connectivity\n' )
    #net.pingFull()

    info( '*** Start capturing pcaps\n' )
    #h0.cmd("tcpdump -i h0-eth9998 -w h0_test.pcap & ")
    h2.cmd("tcpdump -i h2-eth9999 -w h2_test_multiSTA.pcap & ")

    time.sleep(2)

    # info( '*** Video measurement\n' )
    h0.cmd("iperf3 -s -i 1 -p 9999 --cport 9999 | tee sta_VI_CBR_h0.txt &")
    time.sleep(2)
    val = "iperf3 -c 192.168.123.1 -b 20m -M 1024 -Z -p 9999 -t 30 -i 1 --cport 9999 -S 0x4 &"
    h2.cmd(val)

    time.sleep(3)
    
    info( '*** Voice measurement\n' )
    h3.cmd( "iperf3 -s -i 1 -p 9998 | tee sta_VO_CBR_h3.txt &" )
    h2.cmd( "iperf3 -s -i 1 -p 9989 | tee ap_VO_CBR_h4.txt &" )
    h4.cmd( "iperf3 -s -i 1 -p 9994 | tee sta_VO_CBR_h4.txt &" )
    #h2.cmd( "iperf3 -s -i 1 -p 9949 | tee ap_VO_CBR_h5.txt &" )
    # h5.cmd( "iperf3 -s -i 1 -p 9993 | tee sta_VO_CBR_h5.txt &" )
    #h2.cmd( "iperf3 -s -i 1 -p 9939 | tee ap_VO_CBR_h6.txt &" )
    # h6.cmd( "iperf3 -s -i 1 -p 9992 | tee sta_VO_CBR_h6.txt &" )
    h2.cmd( "iperf3 -s -i 1 -p 9929 | tee ap_VO_CBR_h3.txt &" )
    
    time.sleep(2)

    val = "iperf3 -c 192.168.123.4 -u -b 64k -Z --length 160 -p 9998 -t 25 -i 1 --cport 9998 -S 0x6 &"
    h2.cmd(val)
    val = "iperf3 -c 192.168.123.3 -u -b 64k -Z --length 160 -p 9929 -t 25 -i 1 --cport 9929 -S 0x6 &"
    h3.cmd(val)
    # val = "iperf3 -c 192.168.123.7 -u -b 64k -Z --length 160 -p 9992 -t 25 -i 1 --cport 9992 -S 0x6 &"
    # h2.cmd(val)
    #val = "iperf3 -c 192.168.123.3 -u -b 6.4m -Z --length 160 -p 9939 -t 25 -i 1 --cport 9939 -S 0x6 &"
    #h6.cmd(val)
    # val = "iperf3 -c 192.168.123.6 -u -b 64k -Z --length 160 -p 9993 -t 25 -i 1 --cport 9993 -S 0x6 &"
    # h2.cmd(val)
    #val = "iperf3 -c 192.168.123.3 -u -b 6.4m -Z --length 160 -p 9949 -t 25 -i 1 --cport 9949 -S 0x6 &"
    #h5.cmd(val)
    val = "iperf3 -c 192.168.123.5 -u -b 64k -Z --length 160 -p 9994 -t 25 -i 1 --cport 9994 -S 0x6 &"
    h2.cmd(val)
    val = "iperf3 -c 192.168.123.3 -u -b 64k -Z --length 160 -p 9989 -t 25 -i 1 --cport 9989 -S 0x6 &"
    h4.cmd(val)

    time.sleep(3)

    info( '*** BE&BK measurement\n' )
    h7.cmd( "iperf3 -s -i 1 -p 9977 | tee sta_BE_CBR_h7.txt &" )
    h2.cmd( "iperf3 -s -i 1 -p 9979 | tee ap_BE_CBR_h8.txt &" )
    h8.cmd( "iperf3 -s -i 1 -p 9966 | tee sta_BK_CBR_h8.txt &" )
    h2.cmd( "iperf3 -s -i 1 -p 9969 | tee ap_BK_CBR_h7.txt &" )

    time.sleep(2)

    val = "iperf3 -c 192.168.123.3 -M 750 -l 750 -Z -b 250k -p 9969 -t 20 --cport 9666 -i 1 -S 0x1 &"
    h7.cmd(val)
    val = "iperf3 -c 192.168.123.9 -M 750 -l 750 -Z -b 250k -p 9966 -t 20 --cport 9996 -i 1 -S 0x1 &"
    h2.cmd(val)
    val = "iperf3 -c 192.168.123.3 -M 501 -l 501 -Z -b 161k -p 9979 -t 20 --cport 9777 -i 1 -S 0x0 &"
    h8.cmd(val)
    val = "iperf3 -c 192.168.123.8 -M 501 -l 501 -Z -b 161k -p 9977 -t 20 --cport 9997 -i 1 -S 0x0 &"
    h2.cmd(val)

    time.sleep(10)
    #CLI(net)
    
    info("***Ending TCPDump and cleaning up***\n")
    h3.cmd("killall tcpdump")
    h4.cmd("killall tcpdump")
    #h5.cmd("killall tcpdump")
    #h6.cmd("killall tcpdump")
    h2.cmd("killall tcpdump")
    h0.cmd("killall tcpdump")
    h7.cmd("killall tcpdump")
    h8.cmd("killall tcpdump")
    
    h3.cmd("killall iperf3")
    h4.cmd("killall iperf3")
    #h5.cmd("killall iperf3")
    #h6.cmd("killall iperf3")
    h2.cmd("killall iperf3")
    h0.cmd("killall iperf3")
    h7.cmd("killall iperf3")
    h8.cmd("killall iperf3")

    mininet.ns3.stop()      
    mininet.ns3.clear()
    net.stop()

if __name__ == '__main__':
    Main()
    
    
