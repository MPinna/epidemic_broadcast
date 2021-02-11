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

// a lot of imports are just for a rapid reference (by ctrl+click) to inet data structures
import inet.environment.common.PhysicalEnvironment;
import inet.linklayer.acking.AckingWirelessInterface;
import inet.node.base.ApplicationLayerNodeBase;
import inet.node.base.LinkLayerNodeBase;
import inet.node.base.NetworkLayerNodeBase;
import inet.node.base.NodeBase;
import inet.node.base.TransportLayerNodeBase;
import inet.node.inet.AdhocHost;
import inet.node.inet.INetworkNode;
import inet.node.inet.StandardHost;
import inet.node.inet.WirelessHost;
import inet.physicallayer.unitdisk.UnitDiskRadioMedium;
import inet.visualizer.integrated.IntegratedVisualizer;
import inet.physicallayer.contract.packetlevel.IRadioMedium;
import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;


network Floorplan
{
    parameters:
        int numHosts; // number of host in the floorplan
        double height @unit(m); // size of the floorplan
        double width @unit(m);
        @display("bgb=100m,100m");
        
        
        @signal[usersReached](type="long");
        @statistic[coverage](title="Percentage of reached users"; source="usersReached"; record=sum);
        
        @signal[attempts](type="long");
        @statistic[averageAttempts](title="Average attempts";source="attempts";record=mean;);
    submodules:
        host[numHosts]: Host { // hosts array
            @display("p=71,144");
        }
        visualizer: IntegratedVisualizer { // manage the visualization of the hosts and more (wave, range, collisions)
            @display("p=72,22");
        }
        radioMedium: UnitDiskRadioMedium { // the radio medium controller
            @display("p=214,79");
        }
    connections:
}
