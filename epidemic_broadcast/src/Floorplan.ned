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
//
network Floorplan
{
    parameters:
        int numHosts; // number of host in the floorplan
        double height @unit(m); // size of the floorplan
        double width @unit(m);
        @display("bgb=100m,100m");

        @signal[coverage](type="long");
        @statistic[coverageStat](title="Total number of reached users"; source="coverage"; record=sum);

        @signal[timeCoverage](type="int");
        @statistic[timeCoverageStat](title="Number of reached users during time"; source="timeCoverage"; record=vector);
        
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
