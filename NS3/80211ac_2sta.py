
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
    simulationTime = float(cmd.simulationTime)
    distance = float(cmd.distance)
    
    #Configuration arguments
    bandwidth = [20,40,80]
    mcs = [2,4,7]
    gi = [False, True]
    expected_val=[[22,43,92],[41,85,180],[70,140,300]]
    
    print "MCS's: \t Bandwidth: \t Troughput:\t\t  Delay:\t Lost packets:\tTransmited packets:"
    for count_mcs,a in enumerate(mcs):
        for count_bandwidth,b in enumerate(bandwidth):
            for c in gi:
                channel = ns.wifi.YansWifiChannelHelper.Default ()
                phy = ns.wifi.YansWifiPhyHelper.Default ()
                wifi = ns.wifi.WifiHelper ()
                mac = ns.wifi.NqosWifiMacHelper.Default ()

                phy.SetChannel (channel.Create ())
                
                payloadSize = 1472 #bytes
                #ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (payloadSize))

                wifiStaNode = ns.network.NodeContainer ()
                wifiStaNode.Create (2)
                wifiApNode = ns.network.NodeContainer ()
                wifiApNode.Create (1)
                
                wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211ac)

                # Set guard interval
                phy.Set ("ShortGuardEnabled", ns.core.BooleanValue (c))
            

                mac = ns.wifi.VhtWifiMacHelper.Default ()
                DataRate = ns.wifi.VhtWifiMacHelper.DataRateForMcs (a)
                wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager","DataMode", DataRate,
                                                "ControlMode", DataRate)

                ssid = ns.wifi.Ssid ("wifi-80211ac")

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
                myServer=ns.applications.UdpServerHelper (9)
                serverApp = myServer.Install (ns.network.NodeContainer (wifiApNode))
                serverApp.Start (ns.core.Seconds (0.0))
                serverApp.Stop (ns.core.Seconds (simulationTime + 10))

                temp = float((expected_val[count_mcs][count_bandwidth] *1000000)/(payloadSize*8))
                inter =float(1/temp)
                inter = format(inter,'f')

                myClient = ns.applications.UdpClientHelper (apNodeInterface.GetAddress (0), 9)
                myClient.SetAttribute ("MaxPackets", ns.core.UintegerValue (4294967295))
                myClient.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Time (inter))) # packets/s
                myClient.SetAttribute ("PacketSize", ns.core.UintegerValue (payloadSize))

                clientApp = myClient.Install (ns.network.NodeContainer (wifiStaNode))
                clientApp.Start (ns.core.Seconds (0.0))
                clientApp.Stop (ns.core.Seconds (simulationTime + 10))

                ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

                flowmonitor = ns.flow_monitor.FlowMonitorHelper ()
                monitor = flowmonitor.InstallAll ()
                
                monitor.SetAttribute ("StartTime", ns.core.TimeValue (ns.core.Seconds (10)))
                monitor.SetAttribute ("DelayBinWidth", ns.core.DoubleValue (0.001))
                monitor.SetAttribute ("JitterBinWidth", ns.core.DoubleValue (0.001))
                monitor.SetAttribute ("PacketSizeBinWidth", ns.core.DoubleValue (20))
                
                
                ns.core.Simulator.Stop (ns.core.Seconds (simulationTime + 10))
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
                    delay_sum = flow_stats.delaySum
                    delay = delay_sum / p_rec
                    lost_packets = flow_stats.lostPackets

                throughput = 0
                # UDP
                totalPacketsThrough = serverApp.Get (0).GetReceived ()
                throughput = totalPacketsThrough * payloadSize * 8 / (simulationTime * 1000000.0)    # Mbit/s
                
                print a,"\t",b,"MHz\t",c,"\t",throughput,"Mbit/s\t",delay,"\t\t",lost_packets,"\t\t ",p_tran
    return 0

if __name__ == '__main__':
    import sys
sys.exit (main (sys.argv))
