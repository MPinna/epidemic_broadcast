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
#include "inet/common/lifecycle/NodeStatus.h"
#include "inet/common/lifecycle/LifecycleController.h"
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
    //TODO: declare LifecycleController in constructor
    // and instantiate it here

    // self message to be sent to implement
    // syncrhonization to slots
    slotBeep_ = new cMessage("beep");

    // self message to be sent after sending
    // a broadcast to trigger stop operation
    opStop_ = new cMessage("stop");

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

        //TODO: add schedule_at to trigger interface shutdown
        EV<<"opstop to be scheduled at " <<(simTime() + slotLength_) <<endl;
        scheduleAt(simTime() + slotLength_, opStop_);

        //delete packet;
    }
    else
    {
        procUnitStatus_ = LISTENING;
        p_ = par("p");

    }
}

double ProcUnit::getTimeToNextSlot()
{
    return slotLength_ - fmod(simTime().dbl(), slotLength_);
}

void ProcUnit::handleBroadcastMessage(cMessage *msg)
{
    auto parent=this->getParentModule();

    // instantiate LifecycleController and
    // params to allow for operations
    LifecycleController* lifecycleController=new LifecycleController();
    LifecycleOperation::StringMap params;

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

            timeToNextSlot_ = getTimeToNextSlot();
            EV<<"Broadcast attempt in " <<timeToNextSlot_ <<" seconds." <<endl;
            scheduleAt(simTime() + timeToNextSlot_, slotBeep_);

            EV<<"Ricevuto messaggio. Chiamo stopOperation per lanciare moneta" <<endl;
            ModuleStopOperation *stopOperation = new ModuleStopOperation();
            stopOperation->initialize(parent, params);
            lifecycleController->initiateOperation(stopOperation);

            break;
        }
        case(TRANSMITTING):
        {
            EV<<"I already received the message, I am ignoring this one." <<endl;
            break;
        }
        case(SLEEPING):
        {
            EV<<"I am sleeping, I am ignoring everything." <<endl;
            break;
        }
    }
}

void ProcUnit::handleSlotBeepMessage(cMessage *msg)
{
    auto parent=this->getParentModule();

    LifecycleController* lifecycleController=new LifecycleController();
    LifecycleOperation::StringMap params;

    EV<<"Next slot arrived." <<endl;
    EV<<"Flipping a coin." <<endl;
    bool coin = bernoulli(p_);

    attempts_ ++;

    // if heads comes up
    if(coin)
    {
        EV<<"Testa. Chiamo la startOperation per trasmettere il broadcast" <<endl;
        // turn on the interface to allow
        // message broadcast
        ModuleStartOperation *startOperation = new ModuleStartOperation();
        startOperation->initialize(parent, params);
        lifecycleController->initiateOperation(startOperation);

        // should we delete it too since it
        // was created with a 'new' ?
//        delete startOperation;


        EV<<"Heads. Broadcasting the message." <<endl;
        sendPkt((Packet*)broadcast_);
        broadcast_ = nullptr;

        EV<<"Message broadcasted. Going to sleep." <<endl;
        procUnitStatus_ = SLEEPING;

        // schedule interface shutdown to avoid
        // unwanted collision detection
        // Shutdown is scheduled for the next slot and not
        // called immediately to give the module
        // enough time to send out the whole message
        scheduleAt(simTime() + slotLength_, opStop_);

        //emit(attemptsSignal_, attempts_);
    }
    else
    {
        EV<<"Tails. Retrying next slot." <<endl;
        scheduleAt(simTime() + slotLength_, slotBeep_);
    }
}

void ProcUnit::handleStopOperationMessage()
{
    auto parent=this->getParentModule();


    LifecycleController* lifecycleController=new LifecycleController();
    LifecycleOperation::StringMap params;

    EV<<"I am now inside handleStopOperationMessage" <<endl;
    parent->par("stat")="stop";

    ModuleStopOperation *stopOperation = new ModuleStopOperation();
    stopOperation->initialize(parent, params);
    lifecycleController->initiateOperation(stopOperation);
    //parent->getDisplayString().setTagArg("i2", 0, "status/stop"); //change the mini-icon color

}

void ProcUnit::handleMessage(cMessage *msg) // this must take a cMessage
{
    EV<<"The message name is: " <<msg->getName() <<endl;
    auto parent=this->getParentModule();

    // if the message has already been received
    if(!strcmp(parent->par("stat"),"stop"))
        // do nothing
        return;

    // if the message is a broadcast from the outside
    if(msg->isName("COVID"))
    {
        handleBroadcastMessage(msg);
    }

    // if the message is a slot sync timer
    else if(msg->isName("beep"))
    {
        handleSlotBeepMessage(msg);
    }
    // if the message is a stop operation trigger
    else if(msg->isName("stop"))
    {
        handleStopOperationMessage();
    }
    else
    {
        EV<<"Received unknown message type. Ignoring." <<endl;
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
