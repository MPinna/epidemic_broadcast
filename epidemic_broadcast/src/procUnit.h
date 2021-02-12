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

#ifndef __EPIDEMIC_BROADCAST_PROCUNIT_H_
#define __EPIDEMIC_BROADCAST_PROCUNIT_H_

#include "host.h"
#include <omnetpp.h>
#include "inet/common/packet/Packet.h"
#include "inet/common/lifecycle/LifecycleController.h"
#include "inet/common/lifecycle/LifecycleOperation.h"

using namespace omnetpp;
using namespace inet;

/**
 * Represents the node status.
 */
enum Status {
    // the module has not yet received the broadcast message
    LISTENING,

    // broadcast message received, extracting RV to decide whether
    // it should transmit or not
    TRANSMITTING,

    // the module has transmitted the broadcast and will turned off
    SLEEPING
};

/**
 * TODO - Generated class
 */
class ProcUnit : public cSimpleModule
{
    private:
        LifecycleController *lifecycleController;
        LifecycleOperation::StringMap params;

        cMessage* slotBeep_;
        cMessage* opStop_;
        cMessage* broadcast_;

        // node processing unit status
        Status procUnitStatus_;

        // time slot duration parameter in seconds
        double slotLength_;
        double timeToNextSlot_;
        int currentSlot_;

        // success probability for the Bernoulli RV
        double p_;

        // Signal variables to collect statistics //

        // keeps track of the total coverage at the end of the simulation
        simsignal_t coverageSignal_;

        // keeps track of the coverage as function of time
        simsignal_t timeCoverageSignal_;

        // coordinates of parent host signals
        simsignal_t hostXsignal_;
        simsignal_t hostYsignal_;
    protected:
        virtual void initialize();

        virtual double getTimeToNextSlot();
        virtual int getSlotNumberFromCurrentTime();
        virtual void handleMessage(cMessage *msg);
        virtual void handleBroadcastMessage(cMessage *msg);
        virtual void handleSlotBeepMessage(cMessage *msg);
        virtual void handleStopOperationMessage();
        virtual void sendPkt(Packet *packet);

    public:
        ProcUnit();
        ~ProcUnit();
};

#endif
