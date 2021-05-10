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

import inet.physicallayer.unitdisk.UnitDiskRadioMedium;
import inet.visualizer.integrated.IntegratedVisualizer;

//
// Represents the 2D floorplan with N users randomly dropped in it.
//
network Floorplan
{
    parameters:
        int numHosts;				// number of host in the floorplan
        double height @unit(m);		// height of the floorplan
        double width @unit(m);		// width of the floorplan
        @display("bgb=287,197");
        
        
        // only needed (and emitted, check .ini file) for
        // star5to1 validation configuration
        @signal[stateSTransition](type="int");
        @statistic[stateSTransitionStat](title="Current slot number when state S was reached"; source="stateSTransition"; record=last);
		@signal[sleepCoverage](type="int");
		@statistic[sleepCoverageStat](title="Number of sleeping users during each time slot"; source="sleepCoverage"; record=vector);

		// vector statistic needed for every simulation
        @signal[timeCoverage](type="int");
        @statistic[timeCoverageStat](title="Number of reached users during each time slot"; source="timeCoverage"; record=vector);

    submodules:
        host[numHosts]: Host {				// hosts array
            @display("p=63,138");
        }
        visualizer: IntegratedVisualizer {	// manages the visualization of the hosts, waves, range, collisions etc...
            @display("p=64,44");
        }
        radioMedium: UnitDiskRadioMedium {	// the radio medium controller
            @display("p=214,79");
        }
    connections:
}
