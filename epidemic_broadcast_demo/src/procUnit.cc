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
#include "inet/physicallayer/common/packetlevel/Radio.h"
#include "inet/linklayer/common/InterfaceTag_m.h"
#include "inet/linklayer/common/MacAddressTag_m.h"
#include "inet/networklayer/flooding/FloodingHeader_m.h"
#include "inet/networklayer/ipv4/Ipv4Header_m.h"
#include <math.h>       /* modf */

Define_Module(ProcUnit);

using namespace inet;
using namespace physicallayer;


ProcUnit::ProcUnit()
    {
        // Set the pointer to nullptr, so that the destructor won't crash
        // even if initialize() doesn't get called because of a runtime
        // error or user cancellation during the startup process.
        slotBeep_ = broadcast_= nullptr;
    }


ProcUnit::~ProcUnit()
    {
        // Dispose of dynamically allocated the objects
        cancelAndDelete(slotBeep_);
        delete broadcast_;
    }



void ProcUnit::initialize()
{

    slotBeep_ = new cMessage("slotBeep!");
    broadcast_ = nullptr;

    slotLength_ = par("slotLength");

    attempts_ = 0;
    //registerSignal("attempts");
    reachSignal_ = registerSignal("usersReached");

    // if is the first node to transmit, create a packet then send it out
    int init=par("hasInitToken");
    if(init==1){
        procUnitStatus_ = TRANSMITTING;
        auto data = makeShared<ByteCountChunk>(B(1000)); // a generic payload, can't be empty
        inet::Packet *packet=new inet::Packet("COVID", data); // create the packet
        // any supported protocol can be used, but one is needed
        packet->addTag<PacketProtocolTag>()->setProtocol(&Protocol::ipv4);
        auto ipv4Header = makeShared<Ipv4Header>(); // create new ipv4 header
        packet->insertAtFront(ipv4Header); // insert header into packet
        sendPkt(packet);
        procUnitStatus_ = SLEEPING;
        auto parent = this->getParentModule();
        parent->par("stat")="stop";
        parent->getDisplayString().setTagArg("i2", 0, "status/stop"); //change the mini-icon color

        //delete packet;
    }
    else
    {
        procUnitStatus_ = LISTENING;
        p_ = par("p");

    }
}

void ProcUnit::handleMessage(cMessage *msg) // this must take a cMessage
{
    // get the status of the host
    auto parent=this->getParentModule();

    // if the message has already been received
    if(!strcmp(parent->par("stat"),"stop"))
        // do nothing
        return;

    //Radio* radio = (Radio*)getModuleByPath(".wlan.mac.radio");

    // if the msg is a broadcast from the outside
    if(not(msg->isSelfMessage()))
    {
        switch(procUnitStatus_)
        {
            case(LISTENING):
            {
//              //emit()
                EV<<"Broadcast message received while in listening mode. Ok." <<endl;
                procUnitStatus_ = TRANSMITTING;
                broadcast_ = msg;

                parent->par("stat")="green";
                parent->getDisplayString().setTagArg("i2", 0, "status/green"); //change the mini-icon color

                timeToNextSlot_ = slotLength_ - fmod(simTime().dbl(), slotLength_);
                EV<<"Broadcast attempt in " <<timeToNextSlot_ <<" seconds." <<endl;
                scheduleAt(simTime() + timeToNextSlot_, slotBeep_);

                //radio->setRadioMode(inet::physicallayer::Radio::RADIO_MODE_OFF);
            }
            case(TRANSMITTING):
            {
                EV<<"I already received the message, I am ignoring this one." <<endl;
            }
            case(SLEEPING):
            {
                EV<<"I am sleeping, I am ignoring everything." <<endl;
            }
        }
    }
    // if the message is a slot beep
    else
    {
        EV<<"Next slot arrived." <<endl;
        EV<<"Flipping a coin." <<endl;
        bool coin = bernoulli(p_, 0); //TODO: change rng

        attempts_ ++;

        // if heads comes up
        if(coin)
        {
            //radio->setRadioMode(inet::physicallayer::Radio::RADIO_MODE_TRANSMITTER);

            EV<<"Heads. Broadcasting the message." <<endl;
            sendPkt((Packet*)broadcast_);
            broadcast_ = nullptr;

            EV<<"Message broadcasted. Going to sleep." <<endl;
            procUnitStatus_ = SLEEPING;

            parent->par("stat")="stop";
            parent->getDisplayString().setTagArg("i2", 0, "status/stop"); //change the mini-icon color

            //emit(attemptsSignal_, attempts_);
        }
        else
        {
            EV<<"Tails. Retrying next slot." <<endl;
            scheduleAt(simTime() + slotLength_, slotBeep_);
        }
    }


}

void ProcUnit::sendPkt(Packet *packet)
{
    EV<<"sendPkt called" <<endl;
    // a MacAddressReq tag must be set, with at least the destination address
    auto mac = packet->addTag<inet::MacAddressReq>();
    MacAddress *dest=new MacAddress();
    dest->setBroadcast(); // it's a broadcast message
    mac->setDestAddress(*dest);
    send(packet, "out");
}
