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

if __name__ == '__main__':
    setLogLevel( 'info' )
    info( '*** ns-3 network demo\n' )
    net = Mininet()

    bandwidth = 20
    mcs = 3
    gi = False

    info( '*** Creating Network\n' )
    h0 = net.addHost( 'h0' )
    #h1 = net.addHost( 'h1' )
    h2 = net.addHost( 'h2' )

    wifi = WIFISegment()

    payloadSize = 1448  #bytes
    ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (payloadSize))
 
    wifi.wifihelper.SetStandard(ns.wifi.WIFI_PHY_STANDARD_80211n_2_4GHZ)
    ns.core.Config.SetDefault ("ns3::LogDistancePropagationLossModel::ReferenceLoss", ns.core.DoubleValue (40.046))
    
    # Enabling Shor guard intervals:
    wifi.phyhelper.Set("ShortGuardEnabled", ns.core.BooleanValue(gi))
    
    wifi.machelper = ns.wifi.HtWifiMacHelper.Default ()
    
    DataRate = ns.wifi.HtWifiMacHelper.DataRateForMcs (mcs)
    #DataRate = ns.core.StringValue ("HtMcs14")
    
    # set datarate for node h0
    wifi.wifihelper.SetRemoteStationManager( "ns3::ConstantRateWifiManager",
                                             "DataMode", DataRate, "ControlMode", DataRate )
    
    #wifi.wifihelper.SetRemoteStationManager( "ns3::ConstantRateWifiManager",
    #                                         "DataMode", ns.core.StringValue ("VhtMcs4"), "ControlMode", ns.core.StringValue ("VhtMcs4") )
    
    
    #wifi.machelper = ns.wifi.QosWifiMacHelper.Default()
    
    Sssid = "wifi-80211n"
    wifi.addSta( h0, ssid=Sssid )

    # set datarate for node h1
    #wifi.wifihelper.SetRemoteStationManager( "ns3::ConstantRateWifiManager",
    #                                         "DataMode",DataRate, "ControlMode", DataRate )
    #wifi.addSta( h1, ssid=Sssid  )

    wifi.addAp( h2, ssid=Sssid  )

    # set channel bandwidth
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (bandwidth))
    
    if len(sys.argv) > 1:
        wifi.phyhelper.EnablePcap( "80211n_Sta1.pcap", h0.nsNode.GetDevice( 0 ), True, True );
        #wifi.phyhelper.EnablePcap( "Ap-h1.pcap", h1.nsNode.GetDevice( 1 ), True, True );
        wifi.phyhelper.EnablePcap( "80211n_Ap.pcap", h2.nsNode.GetDevice( 0 ), True, True );
    else:
        print('If you want to collect pcap files from this test please run this test with "pcap" argument added')

    info( '*** Configuring hosts\n' )
    h0.setIP('192.168.123.1/24')
    #h1.setIP('192.168.123.2/24')
    h2.setIP('192.168.123.3/24')

    mininet.ns3.start()


    info( '\n *** Testing network connectivity\n' )
    net.pingAll()

    info( '*** Starting TCP iperf server on h2\n' )
    h2.sendCmd( "iperf -s -i 1" )

    info( '*** Testing bandwidth between h0 and h2 while h1 is not transmitting\n' )
    info( '*** Nodes positions: \n' )
    info( 'h0:', mininet.ns3.getPosition( h0 ), '\n' )
    info( 'h2:', mininet.ns3.getPosition( h2 ), '\n' )
    #h2.sendCmd( "iperf -s -i 1" )
    h0.cmdPrint( "iperf -c 192.168.123.3 -i 1" )
    #net.iperf( ( h0, h2 ) )

    #info( '*** Testing bandwidth between h0 and h2 while h1 is also transmitting \n' )
    #h2.sendCmd( "iperf -s" )
    #h1.sendCmd( "iperf -c 192.168.123.3" )
    #h0.cmdPrint( "iperf -c 192.168.123.3" )

    #CLI(net)

