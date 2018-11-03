
import ns.core
import ns.network
import ns.applications
import ns.wifi
import ns.mobility
import ns.internet

def main(argv):
    cmd = ns.core.CommandLine ()
    cmd.simulationTime = 10 #seconds
    cmd.distance = 0.0 #meters
    cmd.frequency = 2.4 #whether 2.4 or 5.0 GHz

    simulationTime = float(cmd.simulationTime)
    distance = float(cmd.distance)
    frequency = float(cmd.frequency)
    
    #Configuration arguments
    bandwidth = 20
    mcs = 3
    gi = True

    print("\n Configured BW:", bandwidth, "MCS:", mcs , "GI:", gi)

    channel = ns.wifi.YansWifiChannelHelper.Default ()
    phy = ns.wifi.YansWifiPhyHelper.Default ()
    wifi = ns.wifi.WifiHelper ()
    mac = ns.wifi.NqosWifiMacHelper.Default ()

    phy.SetChannel (channel.Create ())
    
    payloadSize = 1448  #bytes
    ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (payloadSize))

    wifiStaNode = ns.network.NodeContainer ()
    wifiStaNode.Create (1)
    wifiApNode = ns.network.NodeContainer ()
    wifiApNode.Create (1)
    
    wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211n_2_4GHZ)
    ns.core.Config.SetDefault ("ns3::LogDistancePropagationLossModel::ReferenceLoss", ns.core.DoubleValue (40.046))
    
    # Set guard interval
    phy.Set ("ShortGuardEnabled", ns.core.BooleanValue (gi))
   

    mac = ns.wifi.HtWifiMacHelper.Default ()
    DataRate = ns.wifi.HtWifiMacHelper.DataRateForMcs (mcs)
    wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager","DataMode", DataRate,
                                    "ControlMode", DataRate)

    ssid = ns.wifi.Ssid ("wifi-80211n")

    mac.SetType ("ns3::StaWifiMac",
                    "Ssid", ns.wifi.SsidValue (ssid),
                    "ActiveProbing", ns.core.BooleanValue (False))

    staDevice = wifi.Install (phy, mac, wifiStaNode)
    mac.SetType ("ns3::ApWifiMac",
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

    # Setting applications
    serverApp = ns.network.ApplicationContainer ()
    sinkApp = ns.network.ApplicationContainer ()
    port = 50000
    apLocalAddress = ns.network.Address (ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), port))
    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", apLocalAddress)
    sinkApp = packetSinkHelper.Install (wifiStaNode.Get (0))

    print ("\n Application is starting ! \n")

    sinkApp.Start (ns.core.Seconds (0.0))
    sinkApp.Stop (ns.core.Seconds (simulationTime + 1))

    onoff = ns.applications.OnOffHelper ("ns3::TcpSocketFactory", ns.network.Ipv4Address.GetAny ())
    onoff.SetAttribute ("OnTime",  ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onoff.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    onoff.SetAttribute ("PacketSize", ns.core.UintegerValue (payloadSize))
    onoff.SetAttribute ("DataRate", ns.network.DataRateValue (ns.network.DataRate (1000000000))) # bit/s
    apps = ns.network.ApplicationContainer ()

    remoteAddress = ns.network.AddressValue (ns.network.InetSocketAddress (staNodeInterface.GetAddress (0), port))
    onoff.SetAttribute ("Remote", remoteAddress)
    apps.Add (onoff.Install (wifiApNode.Get (0)))
    apps.Start (ns.core.Seconds (1.0))
    apps.Stop (ns.core.Seconds (simulationTime + 1))

    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

    ns.core.Simulator.Stop (ns.core.Seconds (simulationTime + 1))
    ns.core.Simulator.Run ()
    ns.core.Simulator.Destroy ()

    throughput = 0
    # TCP
    totalPacketsThrough = sinkApp.Get (0).GetTotalRx ()
    throughput = totalPacketsThrough * 8 / (simulationTime * 1000000.0)     # Mbit/s

    print "*** Throughput: " , throughput , " Mbit/s***"
    return 0

if __name__ == '__main__':
    import sys
sys.exit (main (sys.argv))
