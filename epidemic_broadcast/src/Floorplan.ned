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

// numOfHosts: 10
// parametric: true
// static:     false


import inet.environment.common.PhysicalEnvironment;
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


network Floorplan
{	
    parameters:
        int numHosts;
        double dim @unit(m);
		@display("bgb=$dim,$dim,rect");
    submodules:
        host[numHosts]: Host {
            @display("p=178,252");
        }
        visualizer: IntegratedVisualizer { // manage the visualization of the hosts and more (wave, range, collisions)
            @display("p=456.54333,68.14079");
        }
      
}