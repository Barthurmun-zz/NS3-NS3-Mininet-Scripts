
import ns.core
import ns.network
import ns.applications
import ns.wifi
import ns.mobility
import ns.internet
import ns.flow_monitor

def main(argv):
    cmd = ns.core.CommandLine ()
    cmd.simulationTime = 10 #seconds
    cmd.distance = 0.0 #meters
    cmd.frequency = 5.0 #whether 2.4 or 5.0 GHz

    simulationTime = float(cmd.simulationTime)
    distance = float(cmd.distance)
    frequency = float(cmd.frequency)
    
    #Configuration arguments
    udp = True
    bandwidth=[20,40]
    mcs=[2,4,7]
    gi=[False,True]
    expected_val=[[22/2,43/2],[42/2,85/2],[70/2,140/2]]
    
    print "MCS's: \t Bandwidth: \t Troughput:\t\t  Delay:\t Lost packets:\tTransmited packets:"
    for count_mcs,a in enumerate(mcs):
        for count_bandwidth,b in enumerate(bandwidth):
            for c in gi:
                  
                channel = ns.wifi.YansWifiChannelHelper.Default ()
                phy = ns.wifi.YansWifiPhyHelper.Default ()
                wifi = ns.wifi.WifiHelper ()
                mac = ns.wifi.NqosWifiMacHelper.Default ()

                phy.SetChannel (channel.Create ())
                
                if udp == False:
                    payloadSize = 1448  #bytes
                    ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (payloadSize))
                elif udp == True:
                    payloadSize = 1472

                wifiStaNode = ns.network.NodeContainer ()
                wifiStaNode.Create (2)
                wifiApNode = ns.network.NodeContainer ()
                wifiApNode.Create (1)
                
                wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211n_5GHZ)

                # Set guard interval
                phy.Set ("ShortGuardEnabled", ns.core.BooleanValue (c))
            

                mac = ns.wifi.HtWifiMacHelper.Default ()
                DataRate = ns.wifi.HtWifiMacHelper.DataRateForMcs (a)
                wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager","DataMode", DataRate,
                                                "ControlMode", ns.wifi.HtWifiMacHelper.DataRateForMcs (0))

                ssid = ns.wifi.Ssid ("wifi-80211n")

                mac.SetType ("ns3::StaWifiMac",
                                "Ssid", ns.wifi.SsidValue (ssid),
                                "ActiveProbing", ns.core.BooleanValue (False))

                staDevice = wifi.Install (phy, mac, wifiStaNode)
                mac.SetType ("ns3::ApWifiMac",
                                "Ssid", ns.wifi.SsidValue (ssid))

                apDevice = wifi.Install (phy, mac, wifiApNode)

                # Set channel width
                ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (b))

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

                if udp == False:
                    # TCP flow
                    port = 50000
                    apLocalAddress = ns.network.Address (ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), port))
                    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", apLocalAddress)
                    sinkApp = packetSinkHelper.Install (wifiApNode)

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
                    apps.Add (onoff.Install (wifiStaNode))
                    apps.Start (ns.core.Seconds (1.0))
                    apps.Stop (ns.core.Seconds (simulationTime + 1))

                elif udp == True:
                    # UDP flow
                    myServer=ns.applications.UdpServerHelper (9)
                    serverApp = myServer.Install (ns.network.NodeContainer (wifiApNode))
                    serverApp.Start (ns.core.Seconds (0.0))
                    serverApp.Stop (ns.core.Seconds (simulationTime + 1))

                    temp = float((expected_val[count_mcs][count_bandwidth] *1000000)/(payloadSize*8))
                    inter =float(1/temp)
                    inter = format(inter,'f')
                    
                    myClient = ns.applications.UdpClientHelper (apNodeInterface.GetAddress (0), 9)
                    myClient.SetAttribute ("MaxPackets", ns.core.UintegerValue (4294967295))
                    myClient.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Time (inter))) # packets/s
                    myClient.SetAttribute ("PacketSize", ns.core.UintegerValue (payloadSize))

                    clientApp = myClient.Install (ns.network.NodeContainer (wifiStaNode))
                    clientApp.Start (ns.core.Seconds (1.0))
                    clientApp.Stop (ns.core.Seconds (simulationTime + 1))

                ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

                flowmonitor = ns.flow_monitor.FlowMonitorHelper ()
                monitor = flowmonitor.InstallAll ()
                
                monitor.SetAttribute ("StartTime", ns.core.TimeValue (ns.core.Seconds (5)))
                monitor.SetAttribute ("DelayBinWidth", ns.core.DoubleValue (0.001))
                monitor.SetAttribute ("JitterBinWidth", ns.core.DoubleValue (0.001))
                monitor.SetAttribute ("PacketSizeBinWidth", ns.core.DoubleValue (20))
                
                ns.core.Simulator.Stop (ns.core.Seconds (simulationTime))
                ns.core.Simulator.Run ()
                ns.core.Simulator.Destroy ()

                monitor.CheckForLostPackets ()
                classifier = ns.flow_monitor.Ipv4FlowClassifier ()
                classifier = flowmonitor.GetClassifier ()
                stats = monitor.GetFlowStats ()

                for flow_id, flow_stats in stats:
                    t = classifier.FindFlow(flow_id)
                    p_tran = flow_stats.txPackets
                    p_rec = flow_stats.rxPackets
                    p_diff = p_tran - p_rec
                    delay_sum = flow_stats.delaySum
                    delay = delay_sum / p_rec
                    lost_packets = flow_stats.lostPackets

                throughput = 0
                if udp == False:
                    # TCP
                    totalPacketsThrough = sinkApp.Get (0).GetTotalRx ()
                    throughput = totalPacketsThrough * 8 / (simulationTime * 1000000.0) # Mbit/s
                elif udp == True:
                    # UDP
                    totalPacketsThrough = serverApp.Get (0).GetReceived ()
                    throughput = totalPacketsThrough * payloadSize * 8 / (simulationTime * 1000000.0) # Mbit/s
                
                print a,"\t",b,"MHz\t",c,"\t",throughput,"Mbit/s\t",delay,"\t\t",lost_packets,"\t\t ",p_tran
    return 0

if __name__ == '__main__':
    import sys
sys.exit (main (sys.argv))
