//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
// 

package epidemic_broadcast;

import inet.node.base.NodeBase;
import inet.node.inet.WirelessHost;
import inet.mobility.contract.IMobility;
import inet.node.inet.INetworkNode;
import inet.linklayer.acking.AckingWirelessInterface;
import inet.linklayer.contract.IWirelessInterface;
import inet.networklayer.common.InterfaceTable;

//
// Minimal implementation of a wireless network node.
//
module Host extends NodeBase like INetworkNode 
{
    parameters:
        string stat = default("yellow"); // status of the node
        @networkNode;
        @display("i=device/cellphone;i2=status/$stat");

        // the mobility module of the antenna sub-module is implemented by the 
        // mobility module of the host container
        wlan.radio.antenna.mobilityModule = default("^.^.^.mobility");

        // inet network interfaces need an interfaceTable
        wlan.interfaceTableModule = default(absPath(".interfaceTable"));
       
    gates:
        input radioIn @directIn; // needed but never used

    submodules:
		// the wireless interface  allows the node to communicate using the radio medium
        wlan: AckingWirelessInterface { 
            parameters:
                @display("p=375,616,row,150;q=queue");
        }

        // a simple module representing the application logic running on the host
        proc: ProcUnit {
            @display("p=125,240;is=s");
        }

      	// inet network interfaces need an interface table
        interfaceTable: InterfaceTable {
            parameters:
                @display("p=334,222;is=s");
        }
    connections:
        // the procesing units actually communicate with each other using the wlan interface
        proc.in <-- wlan.upperLayerOut;
        proc.out --> wlan.upperLayerIn;
        radioIn --> wlan.radioIn;
}
