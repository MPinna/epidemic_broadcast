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

#include <omnetpp.h>
#include "inet/common/packet/Packet.h"
#include "host.h"

using namespace omnetpp;
using namespace inet;
/**
 * TODO - Generated class
 */


// - LISTENING:the module has not yet received a broadcast
//              message from the outside
// - TRANSMITTING:  the module has received a broadcast message
//                  and on each slot will flip a coin
//                  to decide wheter it should broadcast or not
// - SLEEPING:      the module has transmitted the broadcast and
//                  will be sleeping (actually turned off)
enum Status {LISTENING, TRANSMITTING, SLEEPING};

class ProcUnit : public cSimpleModule
{
    private:
        cMessage* slotBeep_;
        cMessage* opStop_;
        cMessage* broadcast_;

        // used to distinguish between
        // different statuses:
        Status procUnitStatus_;

        double slotLength_;
        double timeToNextSlot_;
        int currentSlot_;

        // used during developement process
        // just to check if the average number
        // of broadcast attempt is consistent
        // with the value of p
        long attempts_;

        // success probability for the
        // Bernoulli variable
        double p_;

        //signal variables
        //TODO: fix code to collect statistics


        // to keep track of the total coverage
        // at the end of the simulation
        simsignal_t coverageSignal_;

        // to keep track of the coverage
        // as function of time
        simsignal_t timeCoverageSignal_;

        // coordinate of parent host signal
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
