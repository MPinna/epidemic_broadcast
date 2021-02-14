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
    delete lifecycleController;
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

/**
 * Called by the simulation kernel when the module receives a
 * message: implements internal logic of the module.
 */
void ProcUnit::handleMessage(cMessage *msg)
{
    if (msg->isName("COVID")) {     // handle COVID broadcast message
        handleBroadcastMessage(msg);
    }
    else if (msg->isName("beep")) { // handle time slot sync message
        handleSlotBeepMessage(msg);
    }
    else if (msg->isName("stop")) { // handle opStop trigger message
        handleStopOperationMessage();
    }
    else {
        EV_DEBUG << "Received unknown message type. Ignoring." << endl;
    }
}

/**
 * Handles received broadcast message.
 */
void ProcUnit::handleBroadcastMessage(cMessage *msg)
{
    // retrieve containing module
    auto parent = this->getParentModule();

    // switch on node processing unit status
    switch(procUnitStatus_)
    {
        case(LISTENING):
        {
            EV_DEBUG << "Broadcast message received while in listening mode. Ok." << endl;

            // retrieve time slot number
            currentSlot_ = getSlotNumberFromCurrentTime();
            EV_DEBUG << "Broadcast message received during time slot n. " << currentSlot_ << endl;

            // emits the long value as a signal
            emit(timeCoverageSignal_, currentSlot_);

            // node processing unit status is not transmitting
            procUnitStatus_ = TRANSMITTING;

            // broadcast message to be re-transmitted
            broadcast_ = msg;

            timeToNextSlot_ = getTimeToNextSlot();
            EV_DEBUG << "Broadcast attempt at " << timeToNextSlot_ << " seconds." <<endl;

            // schedule starting Bernoulli RV extractions at the next time slot
            scheduleAt(simTime() + timeToNextSlot_, slotBeep_);

            // initiate the process of orderly stopping down a module
            ModuleStopOperation *stopOperation = new ModuleStopOperation();
            stopOperation->initialize(parent, params);
            lifecycleController->initiateOperation(stopOperation);

            break;
        }
    }
}

/**
 * Returns the difference between the beginning of the next time
 * slot and the current simulation time.
 */
double ProcUnit::getTimeToNextSlot()
{
    return slotLength_ - fmod(simTime().dbl(), slotLength_);
}

/**
 * Handles the reception of the self message used as timer to sync the
 * procUnit with the time slots.
 */
void ProcUnit::handleSlotBeepMessage(cMessage *msg)
{
    // retrieve containing module
    auto parent = this->getParentModule();

    // flip the coin to decide whether to transmit or not
    EV_DEBUG << "Next time slot started. Flipping the coin." << endl;
    bool success = bernoulli(p_);

    // in case of success
    if (success)
    {
        EV_DEBUG << "Heads. Calling startOperation to turn on radio." << endl;

        // turn on the radio interface to allow transmission of the message broadcast
        ModuleStartOperation *startOperation = new ModuleStartOperation();
        startOperation->initialize(parent, params);
        lifecycleController->initiateOperation(startOperation);

        // send broadcast message and set to null
        EV_DEBUG << "Broadcasting the message." << endl;
        sendPkt((Packet*)broadcast_);
        broadcast_ = nullptr;

        // debugging log message
        EV_DEBUG << "Message broadcasted. Scheduling stop operation." << endl;

        // schedule radio interface shutdown for the next time slot and not
        // to give the module enough time to send out the whole message
        EV_DEBUG << "Scheduling stopOperation for next time slot to shut down radio." << endl;
        scheduleAt(simTime() + slotLength_, opStop_);
    }
    else {
        // in case of failure, schedule a new trial for the next time slot
        EV_DEBUG << "Tails. Retrying next slot." << endl;
        scheduleAt(simTime() + slotLength_, slotBeep_);
    }
}

/**
 * Handle the reception of the self message used to shut down the module
 * and prevent false positive collisions detection when the module is
 * actually powered off.
 */
void ProcUnit::handleStopOperationMessage()
{
    // retrieve containing module
    auto parent = this->getParentModule();

    // update node processing unit status
    procUnitStatus_ = SLEEPING;

    // debugging log
    EV_DEBUG << "Calling stopOperation to permanently shut down module radio interface." << endl;

    // initiate the process of orderly stopping down a module
    ModuleStopOperation *stopOperation = new ModuleStopOperation();
    stopOperation->initialize(parent, params);
    lifecycleController->initiateOperation(stopOperation);
}
