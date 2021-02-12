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

//
// The Processing Unit implements the logic for the behaviour of each host node.
//
simple ProcUnit
{
    parameters:
        // set to 1 if the node is the first one to transmit, 0 otherwise
        int hasInitToken = default(0);
        double slotLength;
         
        // probability of success when extracting Bernoulli RV
		double p = default(0);
         
		@signal[hostX](type=double);
		@signal[hostY](type=double);
        @statistic[hostXstat](source="hostX"; record = last);
        @statistic[hostYstat](source="hostY"; record = last);
     gates:
         // gates to the network interface
        input in;
      	output out;
}
