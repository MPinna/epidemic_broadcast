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

#include "procUnit.h"
#include "inet/linklayer/common/MacAddressTag_m.h"
#include "inet/common/IProtocolRegistrationListener.h"
#include "inet/common/ProtocolTag_m.h"
#include "inet/linklayer/common/InterfaceTag_m.h"
#include "inet/linklayer/common/MacAddressTag_m.h"
#include "inet/networklayer/flooding/FloodingHeader_m.h"
#include "inet/networklayer/ipv4/Ipv4Header_m.h"

Define_Module(ProcUnit);

using namespace inet;
void ProcUnit::initialize()
{
    // if is the first node to transmit, create a packet then send it out
    int init=par("hasInitToken");
    if(init==1){
        auto data = makeShared<ByteCountChunk>(B(1000)); // a generic payload, can't be empty
        inet::Packet *packet=new inet::Packet("test", data); // create the packet
        // any supported protocol can be used, but one is needed
        packet->addTag<PacketProtocolTag>()->setProtocol(&Protocol::ipv4);
        auto ipv4Header = makeShared<Ipv4Header>(); // create new ipv4 header
        packet->insertAtFront(ipv4Header); // insert header into packet
        sendPkt(packet);
    }
}

void ProcUnit::handleMessage(cMessage *msg) // this must take a cMessage
{
    auto parent=this->getParentModule(); // get the status of the host
    if(!strcmp(parent->par("stat"),"green"))
        return; // if the message it's already been received, do nothing
    // otherwise set the status to green, than send out the packet
    parent->par("stat")="green";
    parent->getDisplayString().setTagArg("i2", 0, "status/green"); //change the mini-icon color
    sendPkt((Packet*)msg);
}

void ProcUnit::sendPkt(Packet *packet)
{
    // a MacAddressReq tag must be set, with at least the destination address
    auto mac = packet->addTag<inet::MacAddressReq>();
    MacAddress *dest=new MacAddress();
    dest->setBroadcast(); // it's a broadcast message
    mac->setDestAddress(*dest);
    send(packet, "out");
}


