#Author: Jakub Bryl
#Based on NS3 examples, official documentation 
#Written in python thanks to examples provided by: https://github.com/mohittahiliani/ns-3-python-examples

import ns.core
import ns.network
import ns.applications
import ns.wifi
import ns.mobility
import ns.internet
import ns.flow_monitor
import random

def main(argv):
    simulationTime = 15 #seconds
    distance = 0.0 #meters
    simulationTime = float(simulationTime)
    distance = float(distance)
    
    #Configuration arguments
    bandwidth = 40
    mcs = 3
    gi = False
    expected_val= 54
    
    channel = ns.wifi.YansWifiChannelHelper.Default ()
    phy = ns.wifi.YansWifiPhyHelper.Default ()
    wifi = ns.wifi.WifiHelper ()
    mac = ns.wifi.WifiMacHelper ()

    phy.SetPcapDataLinkType (ns.wifi.WifiPhyHelper.DLT_IEEE802_11_RADIO)
    phy.SetChannel (channel.Create ())
    
    wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211ac)

    wifiStaNode = ns.network.NodeContainer ()
    wifiStaNode.Create (5)
    wifiApNode = ns.network.NodeContainer ()
    wifiApNode.Create (1)

    # Set guard interval
    #phy.Set ("ShortGuardEnabled", ns.core.BooleanValue (gi))


    #mac = ns.wifi.VhtWifiMacHelper.Default ()
    DataRate = "VhtMcs"+str(mcs)

    wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager","DataMode", ns.core.StringValue(DataRate),
                                    "ControlMode", ns.core.StringValue(DataRate))

    ssid = ns.wifi.Ssid ("wifi-80211ac")

    mac.SetType ("ns3::StaWifiMac", "QosSupported", ns.core.BooleanValue (True),
                    "Ssid", ns.wifi.SsidValue (ssid))

    staDevice = wifi.Install (phy, mac, wifiStaNode)

    mac.SetType ("ns3::ApWifiMac","QosSupported", ns.core.BooleanValue (True),
                    "Ssid", ns.wifi.SsidValue (ssid))

    apDevice = wifi.Install (phy, mac, wifiApNode)

    # Set channel width
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (bandwidth))
    
    # mobility
    mobility = ns.mobility.MobilityHelper ()
    positionAlloc = ns.mobility.ListPositionAllocator ()

    positionAlloc.Add (ns.core.Vector3D (0.0, 0.0, 0.0))
    positionAlloc.Add (ns.core.Vector3D (distance, 0.0, 0.0))
    mobility.SetPositionAllocator (positionAlloc)

    mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel")

    mobility.Install (wifiApNode)
    mobility.Install (wifiStaNode)

    # Internet stack
    stack = ns.internet.InternetStackHelper ()
    stack.Install (wifiApNode)
    stack.Install (wifiStaNode)

    address = ns.internet.Ipv4AddressHelper ()

    address.SetBase (ns.network.Ipv4Address ("192.168.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))
    staNodeInterface = address.Assign (staDevice)
    apNodeInterface = address.Assign (apDevice)
    ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (1024))

    # Setting applications
    serverApp = ns.network.ApplicationContainer ()
    sinkApp = ns.network.ApplicationContainer ()
    
    viPort = 9999
    voPort_1 = 9998
    voPort_2 = 9997
    voPort_3 = 9996
    voPort_4 = 9995
    bePort = 9994
    bkPort = 9993
    
    ipv4 = wifiStaNode.Get (0).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    print("Sta IP Addr:")
    print(adr)
    sinkSocket = ns.network.InetSocketAddress (adr, viPort)
    sinkSocket.SetTos (0x4)
    onOffHelper = ns.applications.OnOffHelper ("ns3::TcpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("20Mbps")) #20Mbps
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (1024))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (1.001 + random.uniform(0,0.1))))
    
    serverApp.Add (onOffHelper.Install(wifiApNode.Get(0)))
    
    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiStaNode.Get (0)))
 
    #Voice - 1
    ipv4 = wifiStaNode.Get (1).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    sinkSocket = ns.network.InetSocketAddress (adr, voPort_1)
    sinkSocket.SetTos (0x6)
    onOffHelper=ns.applications.OnOffHelper ("ns3::UdpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("64Kbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (160))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (5.001)))

    serverApp.Add (onOffHelper.Install(wifiApNode.Get(0)))

    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::UdpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiStaNode.Get (1)))
    ##
    ipv4 = wifiApNode.Get (0).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    sinkSocket = ns.network.InetSocketAddress (adr, voPort_1)
    sinkSocket.SetTos (0x6)
    onOffHelper=ns.applications.OnOffHelper ("ns3::UdpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("64Kbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (160))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (5.001+random.uniform(0,0.1))))

    serverApp.Add (onOffHelper.Install(wifiStaNode.Get(1)))

    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::UdpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiApNode.Get (0)))
    

    #Voice - 2
    ipv4 = wifiStaNode.Get (2).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    sinkSocket = ns.network.InetSocketAddress (adr, voPort_2)
    sinkSocket.SetTos (0x6)
    onOffHelper=ns.applications.OnOffHelper ("ns3::UdpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("64Kbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (160))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (5.001)))

    serverApp.Add (onOffHelper.Install(wifiApNode.Get(0)))

    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::UdpSocketFactory", sinkSocket)
    # sinkApp.Add (packetSinkHelper.Install (wifiStaNode.Get (2)))
    ##
    ipv4 = wifiApNode.Get (0).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    sinkSocket = ns.network.InetSocketAddress (adr, voPort_2)
    sinkSocket.SetTos (0x6)
    onOffHelper=ns.applications.OnOffHelper ("ns3::UdpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("64Kbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (160))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (5.001+random.uniform(0,0.1))))

    serverApp.Add (onOffHelper.Install(wifiStaNode.Get(2)))

    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::UdpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiApNode.Get (0))) 

    #BestEffort
    ipv4 = wifiStaNode.Get (3).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    sinkSocket = ns.network.InetSocketAddress (adr, bePort)
    sinkSocket.SetTos (0x0)
    onOffHelper=ns.applications.OnOffHelper ("ns3::TcpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("161Kbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (501))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (10.001+random.uniform(0,0.1))))

    serverApp.Add (onOffHelper.Install(wifiApNode.Get(0)))

    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiStaNode.Get (3)))
    ##
    ipv4 = wifiApNode.Get (0).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    sinkSocket = ns.network.InetSocketAddress (adr, bePort)
    sinkSocket.SetTos (0x0)
    onOffHelper=ns.applications.OnOffHelper ("ns3::TcpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("161Kbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (501))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (10.001+random.uniform(0,0.1))))

    serverApp.Add (onOffHelper.Install(wifiStaNode.Get(3)))

    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiApNode.Get (0)))


    #BackGroun
    ipv4 = wifiStaNode.Get (4).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    sinkSocket = ns.network.InetSocketAddress (adr, bkPort)
    sinkSocket.SetTos (0x1)
    onOffHelper=ns.applications.OnOffHelper ("ns3::TcpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("250Kbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (750))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (10.001+random.uniform(0,0.1))))

    serverApp.Add (onOffHelper.Install(wifiApNode.Get(0)))

    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiStaNode.Get (4)))

    ##
    ipv4 = wifiApNode.Get (0).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    sinkSocket = ns.network.InetSocketAddress (adr, bkPort)
    sinkSocket.SetTos (0x1)
    onOffHelper=ns.applications.OnOffHelper ("ns3::TcpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("250Kbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (750))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (10.001+random.uniform(0,0.1))))

    serverApp.Add (onOffHelper.Install(wifiStaNode.Get(4)))

    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiApNode.Get (0)))

    ##
    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

    phy.EnablePcap( "AP.pcap", apDevice.Get (0))

    ns.core.Simulator.Stop (ns.core.Seconds (simulationTime+1))
    ns.core.Simulator.Run ()

    ns.core.Simulator.Destroy ()
    
    return 0

if __name__ == '__main__':
    import sys
sys.exit (main (sys.argv))
