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
import ns.config_store

def main(argv):
    simulationTime = 40 #seconds
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
    wifiStaNode.Create (1)
    wifiApNode = ns.network.NodeContainer ()
    wifiApNode.Create (1)

    # Set guard interval
    #phy.Set ("ShortGuardEnabled", ns.core.BooleanValue (gi))


    #mac = ns.wifi.VhtWifiMacHelper.Default ()
    DataRate = "VhtMcs"+str(mcs)

    wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager","DataMode", ns.core.StringValue(DataRate),
                                    "ControlMode", ns.core.StringValue(DataRate))

    ssid = ns.wifi.Ssid ("wifi-80211ac")

    mac.SetType ("ns3::StaWifiMac", "Ssid", ns.wifi.SsidValue (ssid), "QosSupported",
                ns.core.BooleanValue (True), "ActiveProbing",  ns.core.BooleanValue (False), "BE_MaxAmsduSize", ns.core.UintegerValue (0),
                "BK_MaxAmsduSize", ns.core.UintegerValue (0),"VI_MaxAmsduSize", ns.core.UintegerValue (0),
                "VO_MaxAmsduSize", ns.core.UintegerValue (0),"BE_MaxAmpduSize", ns.core.UintegerValue (65535),
                "BK_MaxAmpduSize", ns.core.UintegerValue (0),"VI_MaxAmpduSize", ns.core.UintegerValue (65535),
                "VO_MaxAmpduSize", ns.core.UintegerValue (0)) #Default settings

    #mac.SetType ("ns3::StaWifiMac", "QosSupported", ns.core.BooleanValue (True), "Ssid", ns.wifi.SsidValue (ssid))

    staDevice = wifi.Install (phy, mac, wifiStaNode.Get (0))
  
    mac.SetType ("ns3::ApWifiMac","Ssid", ns.wifi.SsidValue (ssid), "QosSupported", 
                ns.core.BooleanValue (True), "BE_MaxAmsduSize", ns.core.UintegerValue (0),
                "BK_MaxAmsduSize", ns.core.UintegerValue (0),"VI_MaxAmsduSize", ns.core.UintegerValue (0),
                "VO_MaxAmsduSize", ns.core.UintegerValue (0),"BE_MaxAmpduSize", ns.core.UintegerValue (65535),
                "BK_MaxAmpduSize", ns.core.UintegerValue (0),"VI_MaxAmpduSize", ns.core.UintegerValue (65535),
                "VO_MaxAmpduSize", ns.core.UintegerValue (0)) #Default settings

   
    apDevice = wifi.Install (phy, mac, wifiApNode.Get (0))

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
    ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (1452))
    print(staNodeInterface)
    print(apNodeInterface)
    # Setting applications
    serverApp = ns.network.ApplicationContainer ()
    sinkApp = ns.network.ApplicationContainer ()
    
    viPort_1 = 9999
    viPort_2 = 9996
    voPort_1 = 9998
    voPort_2 = 9997
    bePort = 9994

    #ToS values: {0x70, 0x28, 0xb8, 0xc0}; //AC_BE, AC_BK, AC_VI, AC_VO

    #Video 1
    ipv4 = wifiStaNode.Get (0).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    print("Sta IP Addr:")
    print(adr)
    sinkSocket = ns.network.InetSocketAddress (adr, viPort_1)
    sinkSocket.SetTos (0xb8)
   
    onOffHelper = ns.applications.OnOffHelper ("ns3::TcpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("11Mbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (1452))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (1.001)))
    serverApp.Add (onOffHelper.Install(wifiApNode.Get (0)))
    
    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiStaNode.Get (0)))
 
    #Voice-1
    ipv4 = wifiStaNode.Get (0).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    sinkSocket = ns.network.InetSocketAddress (adr, voPort_1)
    sinkSocket.SetTos (0xc0)
    onOffHelper=ns.applications.OnOffHelper ("ns3::UdpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("90Kbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (160))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (10.001)))

    serverApp.Add (onOffHelper.Install(wifiApNode.Get(0)))

    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::UdpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiStaNode.Get (0)))
    ##
    ipv4 = wifiApNode.Get (0).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    sinkSocket = ns.network.InetSocketAddress (adr, voPort_2)
    sinkSocket.SetTos (0xc0)
    onOffHelper=ns.applications.OnOffHelper ("ns3::UdpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("90Kbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (160))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (10.001)))

    serverApp.Add (onOffHelper.Install(wifiStaNode.Get(0)))

    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::UdpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiApNode.Get (0)))

    #Video 2
    ipv4 = wifiApNode.Get (0).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    print("AP IP Addr:")
    print(adr)
    sinkSocket = ns.network.InetSocketAddress (adr, viPort_2)
    sinkSocket.SetTos (0xb8)
   
    onOffHelper = ns.applications.OnOffHelper ("ns3::TcpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("5.4Mbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (1452))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (20.001)))
    serverApp.Add (onOffHelper.Install(wifiStaNode.Get (0)))
    
    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiApNode.Get (0)))

    #BestEffort
    ipv4 = wifiStaNode.Get (0).GetObject(ns.internet.Ipv4.GetTypeId ())
    adr = ipv4.GetAddress (1,0).GetLocal ()
    sinkSocket = ns.network.InetSocketAddress (adr, bePort)
    sinkSocket.SetTos (0x70)
    onOffHelper=ns.applications.OnOffHelper ("ns3::TcpSocketFactory", sinkSocket)
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("1Mbps"))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (750))
    onOffHelper.SetAttribute ("StartTime" , ns.core.TimeValue (ns.core.Seconds (30.001)))

    serverApp.Add (onOffHelper.Install(wifiApNode.Get(0)))

    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", sinkSocket)
    sinkApp.Add (packetSinkHelper.Install (wifiStaNode.Get (0)))
    
    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

    phy.EnablePcap( "AP_Scen4_NS3.pcap", apDevice.Get (0))
    phy.EnablePcap( "AP_Scen4STA_NS3.pcap", staDevice.Get (0))

    ns.core.Config.SetDefault ("ns3::ConfigStore::Filename", ns.core.StringValue ("output-attr.txt"))
    ns.core.Config.SetDefault ("ns3::ConfigStore::FileFormat", ns.core.StringValue ("RawText"))
    ns.core.Config.SetDefault ("ns3::ConfigStore::Mode", ns.core.StringValue ("Save"))
    outputConfig = ns.config_store.ConfigStore ()
    outputConfig.ConfigureDefaults ()
    outputConfig.ConfigureAttributes ()
    
    ns.core.Simulator.Stop (ns.core.Seconds (simulationTime+1))
    ns.core.Simulator.Run ()

    ns.core.Simulator.Destroy ()
    
    return 0

if __name__ == '__main__':
    import sys
sys.exit (main (sys.argv))
