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

/**
 * Sets uninitialized pointers to nullptr in order to avoid crashes
 * in the destructor even when the initialize() subroutine isn't
 * called because of a runtime error or user cancellation during the
 * startup process.
 */
ProcUnit::ProcUnit()
{
    slotBeep_ = broadcast_= nullptr;
}

/**
 * Disposes dynamically allocated objects.
 */
ProcUnit::~ProcUnit()
{
    cancelAndDelete(slotBeep_);
    delete opStop_;
    delete broadcast_;
}

/**
 * Called after the module creation.
 */
void ProcUnit::initialize()
{
    //TODO: declare LifecycleController in constructor
    // and instantiate it here

    // self message to be sent to implement synchronization with the time slots
    slotBeep_ = new cMessage("beep");

    // self message to be sent after broadcasting to trigger stop subroutine
    opStop_ = new cMessage("stop");

    // broadcast message: initialized only by the first node
    broadcast_ = nullptr;

    // load time slot duration parameter
    slotLength_ = par("slotLength");

    // register signal for total coverage statistics
    coverageSignal_ = registerSignal("coverage");

    // register signal for coverage as function of time statistics
    timeCoverageSignal_ = registerSignal("timeCoverage");

    // register coordinates of parent host signals
    hostXsignal_ = registerSignal("hostX");
    hostYsignal_ = registerSignal("hostY");

    double parentX = getModuleByPath("^.mobility")->par("initialX");
    double parentY = getModuleByPath("^.mobility")->par("initialY");

    emit(hostXsignal_, parentX);
    emit(hostYsignal_, parentY);

    // retrieve first node to transmit parameter
    int init = par("hasInitToken");

    // if this is the first node to transmit, create a packet then send it out
    if(init == 1) {
        // update node processing status
        procUnitStatus_ = TRANSMITTING;

        // make sure the starter node is counted as reached users
        emit(coverageSignal_, 1);

        // retrieve current simulation time slot
        currentSlot_ = getSlotNumberFromCurrentTime();
        emit(timeCoverageSignal_, currentSlot_);

        // create a generic payload, cannot be empty
        auto data = makeShared<ByteCountChunk>(B(1000));

        // create the INET network packet
        inet::Packet *packet=new inet::Packet("COVID", data);

        // any supported protocol can be used, but one is needed
        packet->addTag<PacketProtocolTag>()->setProtocol(&Protocol::ipv4);

        // create new ipv4 header
        auto ipv4Header = makeShared<Ipv4Header>();

        // insert header into packet
        packet->insertAtFront(ipv4Header);

        sendPkt(packet);
        procUnitStatus_ = SLEEPING;

        // schedule opStop operation to shut down radio
        EV<<"opstop to be scheduled at " <<(simTime() + slotLength_) <<endl;
        scheduleAt(simTime() + slotLength_, opStop_);
    } else {
        // all the other node should be listening
        procUnitStatus_ = LISTENING;
        p_ = par("p");

    }
}

// returns the difference between the
// beginning of the next slot and the
// current sim_time
double ProcUnit::getTimeToNextSlot()
{
    return slotLength_ - fmod(simTime().dbl(), slotLength_);
}

/**
 * Returns the slot number based on the current simulation time.
 */
int ProcUnit::getSlotNumberFromCurrentTime()
{
    int ret = floor(simTime().dbl()/slotLength_ + 1);
    return ret;
}

// handle the reception of a broadcast message
// from the outside
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
//            emit(receptionSignal_)
            EV<<"Broadcast message received while in listening mode. Ok." <<endl;

            emit(coverageSignal_, 1);


            currentSlot_ = getSlotNumberFromCurrentTime();
            EV<<"Broadcast received during slot n. " <<currentSlot_ <<endl;

            emit(timeCoverageSignal_, currentSlot_);

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

        // there should be no need anymore for these last
        // two cases since the procUnit does not
        // listen for incoming messages anymore
        // once it has received the broadcast once
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

// handle the reception of a self message used
// as timer to sync the procUnit with the time slots
void ProcUnit::handleSlotBeepMessage(cMessage *msg)
{
    auto parent=this->getParentModule();

    LifecycleController* lifecycleController=new LifecycleController();
    LifecycleOperation::StringMap params;

    EV<<"Next slot arrived. Flipping a coin." <<endl;
    bool coin = bernoulli(p_);

    attempts_ ++;

    // if heads comes up
    if(coin)
    {
        EV<<"Heads. Calling startOperation to turn on radio." <<endl;
        // turn on the interface to allow
        // message broadcast
        ModuleStartOperation *startOperation = new ModuleStartOperation();
        startOperation->initialize(parent, params);
        lifecycleController->initiateOperation(startOperation);

        // should we delete it too since it
        // was created with a 'new' ?
//        delete startOperation;


        EV<<"Broadcasting the message." <<endl;
        sendPkt((Packet*)broadcast_);
        broadcast_ = nullptr;

        EV<<"Message broadcasted. Going to sleep." <<endl;
        procUnitStatus_ = SLEEPING;

        // schedule interface shutdown to avoid
        // unwanted collision detection
        // Shutdown is scheduled for the next slot and not
        // called immediately to give the module
        // enough time to send out the whole message
        EV<<"Scheduling stopOperation for next slot to shut down radio." <<endl;
        scheduleAt(simTime() + slotLength_, opStop_);

        //emit(attemptsSignal_, attempts_);
    }
    else
    {
        EV<<"Tails. Retrying next slot." <<endl;
        scheduleAt(simTime() + slotLength_, slotBeep_);
    }
}

// handle the reception of a self message used
// to shut down the module and prevent reception
// and collisions detection when the module should
// ignore everything
void ProcUnit::handleStopOperationMessage()
{
    auto parent=this->getParentModule();

    procUnitStatus_ = SLEEPING;


    LifecycleController* lifecycleController=new LifecycleController();
    LifecycleOperation::StringMap params;

    EV<<"Calling stopOperation to permanently shut down radio." <<endl;
    parent->par("stat")="stop";

    ModuleStopOperation *stopOperation = new ModuleStopOperation();
    stopOperation->initialize(parent, params);
    lifecycleController->initiateOperation(stopOperation);
}

void ProcUnit::handleMessage(cMessage *msg) // this must take a cMessage
{
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

// prepare and send a Inet.Packet to the out gate

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
