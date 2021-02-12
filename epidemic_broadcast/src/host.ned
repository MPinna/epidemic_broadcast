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
        //string osgModel = default(""); // 3D model for OSG visualization, no 3D model by default
        //string osgModelColor = default(""); // tint color, no colorization by default
        //string canvasImage = default(""); // image for canvas visualization, no image by default
        //string canvasImageColor = default(""); // tint color, no colorization by default

        // the mobility module of the antenna sub-module is implemented by the 
        // mobility module of the host container
        wlan.radio.antenna.mobilityModule = default("^.^.^.mobility");
        // inet network interfaces needs an interfaceTable
        wlan.interfaceTableModule = default(absPath(".interfaceTable"));
       
    gates:
        input radioIn @directIn; // needed but never used
    submodules:
		
		// the wireless interface  allow the node to communicate by the radio medium
        wlan: AckingWirelessInterface { 
            parameters:
                @display("p=375,616,row,150;q=queue");
        }
        // a simple module representing the appliocation running on the host
        proc: ProcUnit {
            @display("p=125,240;is=s");
        }
      	// inet network interfaces needs an interfaceTable
        interfaceTable: InterfaceTable {
            parameters:
                @display("p=334,222;is=s");
        }
        // mobility module allow us to random place the hosts
//        hostMobility: <default("")> like IMobility if typename != "" {
//          parameters:
//                @display("p=125,160;is=s");
//        }
    connections:
        // the procesing unit actually communicate with other nodes by the wlan interface
        proc.in <-- wlan.upperLayerOut;
        proc.out --> wlan.upperLayerIn;
        radioIn --> wlan.radioIn; // needed but never used

}
