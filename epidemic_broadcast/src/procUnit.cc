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
#include <math.h>

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
    cancelAndDelete(opStop_);
    delete broadcast_;
}

/**
 * Called after the module creation.
 */
void ProcUnit::initialize()
{
    // instantiate LifecycleController and params
    lifecycleController = new LifecycleController();

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
        inet::Packet *packet = new inet::Packet("COVID", data);

        // any supported protocol can be used, IPv4 was chosen
        packet->addTag<PacketProtocolTag>()->setProtocol(&Protocol::ipv4);

        // create new IPv4 header
        auto ipv4Header = makeShared<Ipv4Header>();

        // insert header into INET network packet
        packet->insertAtFront(ipv4Header);

        // send packet
        sendPkt(packet);

        // update node processing unit status
        procUnitStatus_ = SLEEPING;

        // schedule opStop operation to shut down radio
        scheduleAt(simTime() + slotLength_, opStop_);

        // log opStop scheduled
        EV_DEBUG << "opStop scheduled at " << (simTime() + slotLength_) << endl;
    } else {
        // all the other nodes should be listening
        procUnitStatus_ = LISTENING;

        // load Bernoulli RV success probability parameter
        p_ = par("p");
    }
}

/**
 * Processes and sends the given INET network Packet: the MacAddressReq tag must
 * be set for the packet, with at least the destination address
 */
void ProcUnit::sendPkt(Packet *packet)
{
    // retrieve MacAddresspacket Req
    auto macAddressReq = packet->addTag<inet::MacAddressReq>();

    // create new MAC address for broadcast message
    MacAddress *dest = new MacAddress();
    dest->setBroadcast();

    // set MAC address
    macAddressReq->setDestAddress(*dest);

    // send the packet
    send(packet, "out");

    // log packet sent
    EV_DEBUG << "Packet sent." << endl;
}

/**
 * Returns the slot number based on the current simulation time.
 */
int ProcUnit::getSlotNumberFromCurrentTime()
{
    int ret = floor(simTime().dbl()/slotLength_ + 1);
    return ret;
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
        EV_DEBUG<<"Received unknown message type. Ignoring." <<endl;
    }
}

/**
 * Handles received broadcast message.
 */
void ProcUnit::handleBroadcastMessage(cMessage *msg)
{
    auto parent = this->getParentModule();

    // switch on node processing unit status
    switch(procUnitStatus_)
    {
        case(LISTENING):
        {
            EV_DEBUG << "Broadcast message received while in listening mode. Ok." << endl;

            // emits the long value as a signal
            emit(coverageSignal_, 1);

            // retrieve time slot number
            currentSlot_ = getSlotNumberFromCurrentTime();
            EV_DEBUG << "Broadcast message received during time slot n. " << currentSlot_ << endl;

            // emits the long value as a signal
            emit(timeCoverageSignal_, currentSlot_);

            procUnitStatus_ = TRANSMITTING;
            broadcast_ = msg;

            parent->par("stat")="green";
            parent->getDisplayString().setTagArg("i2", 0, "status/green"); //change the mini-icon color

            timeToNextSlot_ = getTimeToNextSlot();
            EV_DEBUG << "Broadcast attempt at " << timeToNextSlot_ << " seconds." <<endl;
            scheduleAt(simTime() + timeToNextSlot_, slotBeep_);

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
            EV_DEBUG<<"I already received the message, I am ignoring this one." <<endl;
            break;
        }
        case(SLEEPING):
        {
            EV_DEBUG<<"I am sleeping, I am ignoring everything." <<endl;
            break;
        }
    }
}

// returns the difference between the
// beginning of the next slot and the
// current sim_time
double ProcUnit::getTimeToNextSlot()
{
    return slotLength_ - fmod(simTime().dbl(), slotLength_);
}

// handle the reception of a self message used
// as timer to sync the procUnit with the time slots
void ProcUnit::handleSlotBeepMessage(cMessage *msg)
{
    auto parent=this->getParentModule();

    LifecycleController* lifecycleController=new LifecycleController();
    LifecycleOperation::StringMap params;

    EV_DEBUG<<"Next slot arrived. Flipping a coin." <<endl;
    bool coin = bernoulli(p_);

    attempts_ ++;

    // if heads comes up
    if(coin)
    {
        EV_DEBUG<<"Heads. Calling startOperation to turn on radio." <<endl;
        // turn on the interface to allow
        // message broadcast
        ModuleStartOperation *startOperation = new ModuleStartOperation();
        startOperation->initialize(parent, params);
        lifecycleController->initiateOperation(startOperation);

        // should we delete it too since it
        // was created with a 'new' ?
//        delete startOperation;


        EV_DEBUG<<"Broadcasting the message." <<endl;
        sendPkt((Packet*)broadcast_);
        broadcast_ = nullptr;

        EV_DEBUG<<"Message broadcasted. Going to sleep." <<endl;
        procUnitStatus_ = SLEEPING;

        // schedule interface shutdown to avoid
        // unwanted collision detection
        // Shutdown is scheduled for the next slot and not
        // called immediately to give the module
        // enough time to send out the whole message
        EV_DEBUG<<"Scheduling stopOperation for next slot to shut down radio." <<endl;
        scheduleAt(simTime() + slotLength_, opStop_);

        //emit(attemptsSignal_, attempts_);
    }
    else
    {
        EV_DEBUG<<"Tails. Retrying next slot." <<endl;
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

    EV_DEBUG<<"Calling stopOperation to permanently shut down radio." <<endl;
    parent->par("stat")="stop";

    ModuleStopOperation *stopOperation = new ModuleStopOperation();
    stopOperation->initialize(parent, params);
    lifecycleController->initiateOperation(stopOperation);
}
