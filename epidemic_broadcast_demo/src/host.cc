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

#include "host.h"

Define_Module(Host);

void Host::initialize()
{
    //setStatus(listening);
    // TODO - Generated method body
}

void Host::handleMessage(cMessage *msg)
{
    EV<<"I am inside Host handleMessage"  <<endl;
    // TODO - Generated method body
}

void Host::setStatus(Status s)
{
    status_ = s;
    /*switch(s)
   / {
        case(listening):
                par("stat")="yellow";
                getDisplayString().setTagArg("i2", 0, "status/yellow");
                return;
        case(transmitting):
                getDisplayString().setTagArg("i2", 0, "status/green");
                par("stat")="green";
                return;
        case(sleeping):
                getDisplayString().setTagArg("i2", 0, "status/red");
                par("stat")="red";
                return;
    }*/
}

Status Host::getStatus()
{
    return status_;
}
